#!/usr/bin/env python3
"""
Build the SA400 LED monitor KiCad project from the Python description.

    python3 gen/build.py            # writes kicad/*, output/BOM.csv, output/ROUTE_REPORT.md

Exit codes:  0 = OK,  1 = crash / DRC failure,  130 = interrupted by the user.
"""
import os
import sys
import json
import time
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C                                  # noqa: E402
from design import build, net_names, key_slot_x     # noqa: E402
from router import Router, RouteError               # noqa: E402
import pcb_writer, sch_writer                       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KICAD = os.path.join(ROOT, "kicad")
OUT = os.path.join(ROOT, "output")
LIB = os.path.join(KICAD, "sa400.pretty")


def main() -> int:
    t0 = time.time()
    fps, net_of_pin = build()
    # KiCad-style names for the no-connect pads so schematic parity is exact
    for fp in fps:
        for p in fp.pads:
            key = f"{fp.ref}.{p.number}"
            if p.net is None and p.number and key in sch_writer.nc_nets(net_of_pin):
                p.net = sch_writer.nc_nets(net_of_pin)[key]
    nets = net_names(fps)
    print(f"[design] {len(fps)} footprints, {len(nets)} nets")

    # ---------------------------------------------------------------- route
    r = Router(fps, key_slot_x())
    signal = [n for n in nets if n not in ("GND", "+5V")]
    # shortest nets first: rank by bounding-box span of terminals
    def span(n):
        cells = r.terminal_cells[n]
        xs = [c[1] for c in cells]; ys = [c[2] for c in cells]
        return (max(xs) - min(xs)) + (max(ys) - min(ys))
    signal.sort(key=span)
    bus = ["WG_n", "DS3_n", "DS2_n", "DS1_n", "DS4_n"]          # constrained: single exit from the fingers
    order = bus + [n for n in signal if n not in bus] + ["+5V", "GND"]
    for n in order:
        w = C.POWER_W if n in ("GND", "+5V") else C.TRACE_W
        r.route_net(n, w)
    print(f"[route] {len(r.segments)} segments, {len(r.via_list)} vias in {time.time() - t0:.1f}s")

    errs = r.drc()
    if errs:
        print("[drc] FAILED:")
        for e in errs:
            print("   ", e)
        return 1
    print("[drc] clean (python geometric check, clearance %.2f mm)" % C.CLEARANCE)

    # ---------------------------------------------------------------- write
    os.makedirs(KICAD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LIB, exist_ok=True)
    pcb_writer.write_pcb(os.path.join(KICAD, f"{C.PROJECT}.kicad_pcb"), fps, nets,
                         r.segments, r.via_list, C.VERSION)
    sch_writer.write_sch(os.path.join(KICAD, f"{C.PROJECT}.kicad_sch"), fps, net_of_pin, C.VERSION)
    written = set()
    for fp in fps:
        name = fp.lib_name.split(":")[1]
        if name not in written:
            pcb_writer.write_kicad_mod(fp, os.path.join(LIB, name + ".kicad_mod"))
            written.add(name)
    dru = os.path.join(KICAD, f"{C.PROJECT}.kicad_dru")
    if os.path.exists(dru):
        os.remove(dru)          # fingers are set back 0.66 mm, so no edge-clearance exception is needed
    sch_writer.write_symbol_lib(os.path.join(KICAD, "sa400.kicad_sym"))
    open(os.path.join(KICAD, "sym-lib-table"), "w").write(
        '(sym_lib_table\n  (version 7)\n'
        '  (lib (name "sa400")(type "KiCad")(uri "${KIPRJMOD}/sa400.kicad_sym")(options "")(descr "Project symbols"))\n)\n')
    write_project(os.path.join(KICAD, f"{C.PROJECT}.kicad_pro"))
    open(os.path.join(KICAD, "fp-lib-table"), "w").write(
        '(fp_lib_table\n  (version 7)\n'
        '  (lib (name "sa400")(type "KiCad")(uri "${KIPRJMOD}/sa400.pretty")(options "")(descr "Project footprints"))\n)\n')
    write_bom(fps, os.path.join(OUT, "BOM.csv"))
    write_jlc_bom(fps, os.path.join(OUT, "assembly", "BOM_jlcpcb.csv"))
    write_report(r, nets, os.path.join(OUT, "ROUTE_REPORT.md"))
    print(f"[done] {time.time() - t0:.1f}s")
    return 0


def write_project(path):
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.4},
                "rules": {
                    "min_clearance": C.CLEARANCE, "min_copper_edge_clearance": 0.3,
                    "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25, "min_microvia_diameter": 0.2,
                    "min_microvia_drill": 0.1, "min_resolved_spokes": 2, "min_silk_clearance": 0.0,
                    "min_text_height": 0.8, "min_text_thickness": 0.08, "min_through_hole_diameter": 0.3,
                    "min_track_width": 0.15, "min_via_annular_width": 0.13, "min_via_diameter": 0.6,
                    "solder_mask_to_copper_clearance": 0.0, "use_height_for_length_calcs": True,
                },
                "track_widths": [0.0, 0.4, 0.6, 1.0],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.8, "drill": 0.4}],
            },
            "layer_presets": [], "viewports": [],
        },
        "boards": [], "cvpcb": {"equivalence_files": []}, "libraries": {"pinned_footprint_libs": [],
                                                                        "pinned_symbol_libs": []},
        "meta": {"filename": f"{C.PROJECT}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [{
                "bus_width": 12, "clearance": C.CLEARANCE, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
                "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
                "name": "Default", "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
                "track_width": C.TRACE_W, "via_diameter": C.VIA_DIA, "via_drill": C.VIA_DRILL, "wire_width": 6,
            }],
            "meta": {"version": 3},
            "net_colors": None, "netclass_assignments": None, "netclass_patterns": [],
        },
        "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "gerbers/", "pos_files": "",
                                  "specctra_dsn": "", "step": "", "svg": "", "vrml": ""}, "page_layout_descr_file": ""},
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[sch_writer.PROJ_UUID, ""]],
        "text_variables": {},
    }
    json.dump(pro, open(path, "w"), indent=2)


def write_bom(fps, path):
    rows = {}
    for fp in fps:
        if fp.ref.startswith("H") or fp.ref == "J1":
            continue
        key = (fp.value, fp.lib_name)
        rows.setdefault(key, []).append(fp.ref)
    notes = {
        "74LS14": "TI SN74LS14N or equiv. DIP-14. https://www.ti.com/product/SN74LS14",
        "74LS00": "TI SN74LS00N or equiv. DIP-14. https://www.ti.com/product/SN74LS00",
        "74LS06": "TI SN74LS06N or equiv. DIP-14, open-collector. https://www.ti.com/product/SN74LS06",
        "RED": "5 mm red LED, standard brightness e.g. Kingbright L-53ID (LCSC C598429); high-efficiency WP7113LID also fits (then use 1k5)",
        "GREEN": "5 mm green LED, standard brightness e.g. Kingbright WP7113GD (LCSC C7117617); high-efficiency WP7113LGD also fits (then use 1k5)",
        "2k2": "1/4 W axial. +12 V indicator series (~4.5 mA).",
        "10k": "1/4 W axial 5%",
        "100nF": "Ceramic disc 50 V, 2.5 mm pitch",
        "10uF/16V": "Electrolytic radial 5 mm dia, 2.5 mm pitch",
        "AMP 1-641737-1": "TE Commercial MATE-N-LOK 4-pos RIGHT-ANGLE header 1-641737-1 https://www.te.com/en/product-1-641737-1.html ; vertical 350211-1 (LCSC C305826) fits the same pads",
        "470R": "1/4 W axial 5%. LED series (R1-R8, R21, ~5.5 mA) and bus series / fault-limiting (R14-R18).",
        "PTC 0.5A": "Radial PTC resettable fuse, 0.5 A hold / 1 A trip, 16 V+, 5.08 mm, e.g. Littelfuse RUEF050 https://www.mouser.com/c/?q=RUEF050",
        "IRF4905PBF": "P-channel MOSFET, 55 V, 20 mOhm, TO-220 pins G-D-S (LCSC C2564) https://www.mouser.com/c/?q=IRF4905PBF ; onsemi NDP6020P is an equivalent G-D-S part",
        "1N5339B": "Zener 5.6 V 5 W, DO-15 https://www.mouser.com/c/?q=1N5339B",
        "YELLOW": "5 mm yellow LED, standard brightness e.g. Kingbright WP483YDT (LCSC C6001325)",
            }
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Qty", "References", "Value", "Footprint", "Notes / source"])
        for (value, lib), refs in sorted(rows.items(), key=lambda kv: kv[1][0]):
            w.writerow([len(refs), " ".join(sorted(refs, key=lambda s: (s[0], int(s[1:])))), value, lib,
                        notes.get(value, "")])
        w.writerow([4, "H1 H2 H3 H4", "M3 standoff + screw", "MountingHole_3.2mm_M3", "Standalone board mounting"])
        w.writerow([3, "U1 U2 U3 (optional)", "DIP-14 socket", "", "Recommended for hand assembly"])


# JLCPCB parts as matched for the v0.2.2 PCBA order (2026-09/10): (LCSC part number, manufacturer part / note).
# Keyed by schematic value; a value missing here is left for JLCPCB's matcher.
JLC = {
    "74LS14":       ("C73064",     "TI SN74LS14N; fit into socket U1A"),
    "74LS00":       ("C181629",    "TI SN74LS00N; fit into socket U2A"),
    "74LS06":       ("C22384767",  "TI SN74LS06N(LX); fit into socket U3A"),
    "RED":          ("C598429",    "Kingbright L-53ID 5mm red; cathode = square pad"),
    "GREEN":        ("C7117617",   "Kingbright WP7113GD 5mm green; cathode = square pad"),
    "YELLOW":       ("C6001325",   "Kingbright WP483YDT 5mm yellow; cathode = square pad"),
    "470R":         ("C176518",    "YAGEO MFR-25JT-52-470R 1/4W 5%"),
    "10k":          ("C176451",    "YAGEO MFR-25JT-52-10K 1/4W 5%"),
    "2k2":          ("C172997",    "YAGEO MFR-25FTE52-2K2 1/4W 1%"),
    "100nF":        ("C45664",     "100nF 50V ceramic disc (2.0mm pitch is OK on the 2.54mm pads)"),
    "10uF/16V":     ("C53330112",  "10uF 16V radial 5mm; + lead in the square pad"),
    "AMP 1-641737-1": ("", "TE 1-641737-1 Commercial Mate-N-Lok 4-pos RIGHT-ANGLE header, TOP side, mating face at the rear edge, pin 1 = square pad. If not stocked: vertical 350211-1 = LCSC C305826 on the same pads"),
    "PTC 0.5A":     ("C135425",    "A72-050 PTC resettable fuse 0.5A hold"),
    "IRF4905PBF":   ("C2564",      "P-MOSFET TO-220 pin order G-D-S; gate = square pad; tab toward the J2 edge"),
    "1N5339B":      ("C5444832",   "Zener 5.6V 5W; band (cathode) = square pad"),
}
SOCKET = ("DIP-14 socket", "U1A,U2A,U3A", "DIP-14_W7.62mm", "C190815",
          "DIP-14 socket soldered under U1/U2/U3 (same positions as the ICs)")


def write_jlc_bom(fps, path):
    """JLCPCB BOM: Comment, Designator, Footprint, LCSC Part #, notes.

    Sockets are listed as U1A/U2A/U3A (JLCPCB's own naming from the order review); verify.py adds
    matching CPL rows at the IC positions so the upload has no duplicate designators.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = {}
    for fp in fps:
        if fp.ref == "J1" or fp.ref.startswith("H"):
            continue
        rows.setdefault((fp.value, fp.lib_name.split(":")[1]), []).append(fp.ref)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Manufacturer part / notes"])
        for (val, fpn), refs in sorted(rows.items(), key=lambda kv: (kv[1][0][0], int(kv[1][0][1:]))):
            lcsc, note = JLC.get(val, ("", ""))
            w.writerow([val, ",".join(sorted(refs, key=lambda s: (s[0], int(s[1:])))), fpn, lcsc, note])
        w.writerow(list(SOCKET))


def write_report(r, nets, path):
    lines = [f"# Route report - {C.PROJECT} v{C.VERSION}", "",
             f"- grid {C.GRID} mm, clearance {C.CLEARANCE} mm, signal {C.TRACE_W} mm, power {C.POWER_W} mm",
             f"- segments: {len(r.segments)}, vias: {len(r.via_list)}", "", "| net | segments | vias | length mm |",
             "|---|---|---|---|"]
    for n in nets:
        segs = [s for s in r.segments if s[0] == n]
        L = sum(abs(s[4] - s[2]) + abs(s[5] - s[3]) for s in segs)
        v = sum(1 for x in r.via_list if x[0] == n)
        lines.append(f"| {n} | {len(segs)} | {v} | {L:.1f} |")
    open(path, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[build] interrupted by user", file=sys.stderr)
        sys.exit(130)
    except (RouteError, Exception) as e:      # crash -> exit 1, distinct from Ctrl-C
        import traceback
        traceback.print_exc()
        print(f"[build] FAILED: {e}", file=sys.stderr)
        sys.exit(1)
