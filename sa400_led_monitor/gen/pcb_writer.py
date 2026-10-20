"""
Writes a .kicad_pcb (format version 20221018 = KiCad 7.0; KiCad 8 and 9
open it and migrate silently) plus the custom footprints as .kicad_mod.
"""
import uuid
import datetime
from typing import List, Dict
import config as C
from design import Footprint, Pad, key_slot_x, tab_left
import sch_writer

STD_LAYERS = """    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)"""


def u():
    return str(uuid.uuid4())


def f(x: float) -> str:
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def side(layer: str, name: str) -> str:
    """Map a front-side layer name to the footprint's side."""
    if layer == "B.Cu":
        return name.replace("F.", "B.")
    return name


def fp_graphics(fp: Footprint, layer_prefix_silk: str, layer_prefix_fab: str, rel) -> List[str]:
    out = []
    for item in fp.silk:
        kind = item[0]
        if kind == "line":
            _, x1, y1, x2, y2 = item
            x1, y1 = rel(x1, y1); x2, y2 = rel(x2, y2)
            out.append(f'    (fp_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                       f'(stroke (width 0.12) (type solid)) (layer "{layer_prefix_silk}") (tstamp {u()}))')
        elif kind == "rect":
            _, x1, y1, x2, y2 = item
            x1, y1 = rel(x1, y1); x2, y2 = rel(x2, y2)
            out.append(f'    (fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                       f'(stroke (width 0.12) (type solid)) (fill none) (layer "{layer_prefix_silk}") (tstamp {u()}))')
        elif kind == "circle":
            _, cx, cy, r = item
            cx, cy = rel(cx, cy)
            out.append(f'    (fp_circle (center {f(cx)} {f(cy)}) (end {f(cx + r)} {f(cy)}) '
                       f'(stroke (width 0.12) (type solid)) (fill none) (layer "{layer_prefix_silk}") (tstamp {u()}))')
        elif kind == "arc":
            _, cx, cy, r = item   # semicircle notch opening to the right, drawn as arc
            cx, cy = rel(cx, cy)
            out.append(f'    (fp_arc (start {f(cx)} {f(cy - r)}) (mid {f(cx + r)} {f(cy)}) (end {f(cx)} {f(cy + r)}) '
                       f'(stroke (width 0.12) (type solid)) (layer "{layer_prefix_silk}") (tstamp {u()}))')
        elif kind == "text":
            _, x, y, s, size = item
            x, y = rel(x, y)
            out.append(f'    (fp_text user "{s}" (at {f(x)} {f(y)}) (layer "{layer_prefix_silk}") '
                       f'(effects (font (size {f(size)} {f(size)}) (thickness 0.12))) (tstamp {u()}))')
    for item in fp.fab:
        if item[0] == "rect":
            _, x1, y1, x2, y2 = item
            x1, y1 = rel(x1, y1); x2, y2 = rel(x2, y2)
            out.append(f'    (fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                       f'(stroke (width 0.1) (type solid)) (fill none) (layer "{layer_prefix_fab}") (tstamp {u()}))')
    if fp.courtyard:
        x1, y1, x2, y2 = fp.courtyard
        x1, y1 = rel(x1, y1); x2, y2 = rel(x2, y2)
        crt = "F.CrtYd"
        out.append(f'    (fp_rect (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                   f'(stroke (width 0.05) (type solid)) (fill none) (layer "{crt}") (tstamp {u()}))')
    return out


def pad_sexpr(p: Pad, rel, net_ids: Dict[str, int], flip: bool) -> str:
    x, y = rel(p.x, p.y)
    kind = "thru_hole" if p.drill is not None and p.number else "np_thru_hole" if p.drill else "smd"
    shape = p.shape
    layers = " ".join(f'"{l}"' for l in p.layers)
    s = f'    (pad "{p.number}" {kind} {shape} (at {f(x)} {f(y)}) (size {f(p.size[0])} {f(p.size[1])})'
    if p.drill is not None:
        s += f' (drill {f(p.drill)})'
    s += f' (layers {layers})'
    if kind == "smd":
        s += ' (solder_mask_margin 0.05)'
    if p.net and p.number:
        s += f' (net {net_ids[p.net]} "{p.net}")'
    s += f' (tstamp {u()}))'
    return s


def footprint_sexpr(fp: Footprint, net_ids: Dict[str, int], embedded=True, mirror_y=None) -> str:
    flip = fp.layer == "B.Cu" if mirror_y is None else mirror_y

    def rel(x, y):
        # Geometry in design.py is the INTENDED absolute geometry as seen from the top.
        # Back-side footprints are written front-side with y mirrored about the footprint
        # origin; gen/postprocess.py then lets KiCad flip them TOP_BOTTOM, which un-mirrors
        # y and swaps layers, so the board shows exactly the intended geometry.  The library
        # copy is written the same (mirrored) way so KiCad's flipped-library comparison matches.
        lx, ly = x - fp.x, y - fp.y
        return (lx, -ly) if flip else (lx, ly)

    silk, fab = "F.SilkS", "F.Fab"      # always written front-side; see rel()
    # reference above the courtyard (front) / below it (back, where the housing is not)
    ref_y = (fp.courtyard[1] - fp.y - 1.0) if fp.courtyard else -3
    if flip and fp.courtyard:
        ref_y = -(fp.courtyard[3] - fp.y + 1.0)      # pre-flip local; lands below the part after the flip
    lines = []
    head = f'(footprint "{fp.lib_name}" (layer "F.Cu")' if embedded else f'(footprint "{fp.lib_name.split(":")[1]}"'
    lines.append(head)
    lines.append(f'    (tstamp {u()})' if embedded else '    (version 20221018) (generator sa400_gen)')
    if embedded:
        lines.append(f'    (at {f(fp.x)} {f(fp.y)}{"" if fp.rot == 0 else " " + f(fp.rot)})')
    lines.append(f'    (descr "{fp.description}")')
    if embedded:
        # link to the schematic symbol.  For a root-sheet symbol KiCad uses "/<symbol uuid>"
        # (verified against KiCad 10's own demos/ecc83 project); the root sheet UUID is NOT part of it.
        lines.append(f'    (path "/{sch_writer.symbol_uuid(fp.ref)}")')
    lines.append('    (attr through_hole)' if any(p.drill for p in fp.pads) else '    (attr smd)')
    mirror = ''
    ref_at = f"0 {f(ref_y)}" if fp.ref_rot == 0 else f"-1.6 {f(ref_y + 6.0)} {f(fp.ref_rot)}"
    if fp.ref_pos:
        rx, ry = rel(fp.x + fp.ref_pos[0], fp.y + fp.ref_pos[1])
        ref_at = f"{f(rx)} {f(ry)} {f(fp.ref_pos[2])}"
    lines.append(f'    (fp_text reference "{fp.ref}" (at {ref_at}) (layer "{silk}")'
                 f' (effects (font (size 1 1) (thickness 0.15)){mirror}) (tstamp {u()}))')
    lines.append(f'    (fp_text value "{fp.value}" (at 0 {f(ref_y + 1.5)}) (layer "{fab}")'
                 f' (effects (font (size 1 1) (thickness 0.15)){mirror}) (tstamp {u()}))')
    lines += fp_graphics(fp, silk, fab, rel)
    for p in fp.pads:
        lines.append(pad_sexpr(p, rel, net_ids, flip))
    lines.append(')')
    return "\n".join(lines)


MIRROR_LIB = False


def write_kicad_mod(fp: Footprint, path: str):
    """Standalone footprint file for the project library (front-side canonical form).
    A footprint the board carries on B.Cu was flipped by KiCad's left-right mirror, so the
    library (front) version is the board version with x negated."""
    if False:
        def mx(x): return 2 * fp.x - x
        pads = [Pad(q.number, mx(q.x), q.y, q.shape, q.size, q.drill, q.layers, q.net) for q in fp.pads]
        silk = []
        for it in fp.silk:
            if it[0] in ("line",):
                silk.append((it[0], mx(it[1]), it[2], mx(it[3]), it[4]))
            elif it[0] == "rect":
                silk.append((it[0], mx(it[3]), it[2], mx(it[1]), it[4]))
            elif it[0] in ("circle", "arc"):
                silk.append((it[0], mx(it[1]), it[2], it[3]))
            elif it[0] == "text":
                silk.append((it[0], mx(it[1]), it[2], it[3], it[4]))
        cy = fp.courtyard
        crt = (mx(cy[2]), cy[1], mx(cy[0]), cy[3]) if cy else None
        fp = Footprint(fp.ref, fp.value, fp.lib_name, fp.x, fp.y, 0, "F.Cu", pads, silk, list(fp.fab), crt, fp.description)
    fp2 = Footprint(fp.ref, fp.value, fp.lib_name, fp.x, fp.y, 0, "F.Cu", fp.pads, fp.silk, fp.fab,
                    fp.courtyard, fp.description)
    fp2.ref_rot, fp2.ref_pos = fp.ref_rot, fp.ref_pos      # same reference placement as the board copy
    net_ids = {}
    pads_bak = [(p.net) for p in fp.pads]
    for p in fp.pads:
        p.net = None
    txt = footprint_sexpr(fp2, net_ids, embedded=False, mirror_y=(fp.layer == "B.Cu"))
    for p, n in zip(fp.pads, pads_bak):
        p.net = n
    open(path, "w").write(txt + "\n")


def write_pcb(path: str, fps: List[Footprint], nets: List[str], segments, vias, version: str):
    net_ids = {n: i + 1 for i, n in enumerate(nets)}
    W, H = C.BOARD_W, C.BOARD_H
    ks_x, ks_w, ks_d = key_slot_x(), C.J1_KEY_SLOT_W, C.J1_KEY_SLOT_DEPTH
    today = datetime.date.today().isoformat()
    out = []
    out.append('(kicad_pcb (version 20221018) (generator pcbnew)')
    out.append(f'  (general (thickness {f(C.BOARD_THICKNESS)}))')
    out.append('  (paper "A3")')
    out.append(f'  (title_block (title "{C.TITLE}") (date "{today}") (rev "v{version}") '
               f'(company "Ven") (comment 1 "Generated by gen/build.py - do not hand-edit without bumping VERSION") '
               f'(comment 2 "Card edge: J1 pin 2 at the right, viewed from component side, fingers pointing away") '
               f'(comment 3 "J2 AMP Mate-N-Lok 350211-1 on the solder side, SA400 pinout: +5V logic supply (PTC, P-FET, clamp), +12V indicator"))')
    out.append('  (layers')
    out.append(STD_LAYERS)
    out.append('  )')
    out.append(f'''  (setup
    (pad_to_mask_clearance 0.05)
    (grid_origin 0 0)
    (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros false) (usegerberextensions true) (usegerberattributes true)
      (usegerberadvancedattributes true) (creategerberjobfile true) (dashed_line_dash_ratio 12.000000)
      (dashed_line_gap_ratio 3.000000) (svgprecision 4) (plotframeref false) (viasonmask false)
      (mode 1) (useauxorigin false) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15.000000)
      (dxfpolygonmode false) (dxfimperialunits true) (dxfusepcbnewfont true) (psnegative false)
      (psa4output false) (plotreference true) (plotvalue false) (plotinvisibletext false) (sketchpadsonfab false)
      (subtractmaskfromsilk true) (outputformat 1) (mirror false) (drillshape 0) (scaleselection 1)
      (outputdirectory "gerbers/"))
  )''')
    out.append('  (net 0 "")')
    for n in nets:
        out.append(f'  (net {net_ids[n]} "{n}")')
    for fp in fps:
        out.append("  " + footprint_sexpr(fp, net_ids).replace("\n", "\n  "))

    # ---- board outline with key slot notch on the top (rear) edge
    def gl(x1, y1, x2, y2):
        out.append(f'  (gr_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
                   f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts") (tstamp {u()}))')
    tl, tr, R = tab_left(), C.J1_TAB_RIGHT, C.J1_REAR_RECESS
    gl(0, R, tl, R)
    rc = C.J1_TAB_CORNER_R
    def ga(sx, sy, mx, my, ex, ey):
        out.append(f'  (gr_arc (start {f(sx)} {f(sy)}) (mid {f(mx)} {f(my)}) (end {f(ex)} {f(ey)}) '
                   f'(stroke (width 0.1) (type default)) (layer "Edge.Cuts") (tstamp {u()}))')
    k = rc * (1 - 0.7071)
    gl(tl, R, tl, rc)
    if rc > 0:
        ga(tl, rc, tl + k, k, tl + rc, 0)
    if C.J1_KEY_SLOT:
        xl, xr = ks_x - ks_w / 2, ks_x + ks_w / 2
        gl(tl + rc, 0, xl, 0); gl(xl, 0, xl, ks_d); gl(xl, ks_d, xr, ks_d); gl(xr, ks_d, xr, 0); gl(xr, 0, tr - rc, 0)
    else:
        gl(tl + rc, 0, tr - rc, 0)
    if rc > 0:
        ga(tr - rc, 0, tr - k, k, tr, rc)
    gl(tr, rc, tr, R)
    gl(tr, R, W, R)
    gl(W, R, W, H)
    gl(W, H, 0, H)
    gl(0, H, 0, R)

    # ---- board text
    def txt(x, y, s, size=1.5, layer="F.SilkS", mirror=False, bold=False):
        eff = f'(font (size {f(size)} {f(size)}) (thickness {f(size*0.15)}){" bold" if bold else ""})'
        eff += ' (justify left mirror)' if mirror else ' (justify left)'
        out.append(f'  (gr_text "{s}" (at {f(x)} {f(y)}) (layer "{layer}") (effects {eff}) (tstamp {u()}))')
    txt(6, 50, f"{C.PROJECT} v{version}", 2.0, bold=True)
    txt(6, 53.5, "SA400 form-factor drive-select / write-gate monitor", 1.3)
    txt(6, 56, "RED = drive selected   GREEN = write gate asserted", 1.3)
    txt(6, 58.5, "High-impedance tap: NO terminators on this board", 1.0)
    txt(50, 46.0, "12V", 0.9); txt(61, 46.0, "5V", 0.9)
    txt(6, 61, "COMPONENT SIDE  -  J1 pin 2 at right, fingers point away", 1.0)
    txt(tl - 48, 13.0, "J1  34-pin Shugart bus  (pin 2 at right ->)", 1.0)
    # J2 labels are part of the footprint (component side, below the housing) since v0.2.4
    for n in range(4):
        x = C.MOUNT_HOLES[0][0] + 24.13 + n * 25.4
        txt(x - 2.0, 124.5, f"DRIVE {n + 1}", 1.2, bold=True)
        txt(x - 3.3, 113.0, "SEL", 0.9)
        txt(x + 1.8, 113.0, "WR", 0.9)
    txt(W - 60, H - 3, f"{C.PROJECT} v{version}", 1.2, layer="B.SilkS", mirror=True)

    # ---- traces / vias
    for net, layer, x1, y1, x2, y2, w in segments:
        lname = "F.Cu" if layer == 0 else "B.Cu"
        out.append(f'  (segment (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) (width {f(w)}) '
                   f'(layer "{lname}") (net {net_ids[net]}) (tstamp {u()}))')
    for net, x, y in vias:
        out.append(f'  (via (at {f(x)} {f(y)}) (size {f(C.VIA_DIA)}) (drill {f(C.VIA_DRILL)}) '
                   f'(layers "F.Cu" "B.Cu") (net {net_ids[net]}) (tstamp {u()}))')

    # ---- GND pour on B.Cu (unfilled; press B in KiCad to fill)
    m = 1.0
    pts = [(m, C.J1_FINGER_DEPTH + 2.0), (W - 48, C.J1_FINGER_DEPTH + 2.0), (W - 48, m + 1.0),
           (W - m, m + 1.0)]
    # keep the pour clear of the finger area on the solder side too
    poly = [(m, C.J1_FINGER_DEPTH + 3), (W - 50, C.J1_FINGER_DEPTH + 3), (W - 50, m), (W - m, m) ,
            (W - m, H - m), (m, H - m)]
    poly = [(m, R + m), (W - m, R + m),
            (W - m, H - m), (m, H - m)]
    pts_s = " ".join(f"(xy {f(x)} {f(y)})" for x, y in poly)
    out.append(f'  (zone (net {net_ids["GND"]}) (net_name "GND") (layer "B.Cu") (tstamp {u()}) '
               f'(hatch edge 0.5) (connect_pads (clearance 0.3)) (min_thickness 0.25) '
               f'(filled_areas_thickness no) (fill yes (thermal_gap 0.5) (thermal_bridge_width 0.5)) '
               f'(polygon (pts {pts_s})))')
    out.append(')')
    open(path, "w").write("\n".join(out) + "\n")
