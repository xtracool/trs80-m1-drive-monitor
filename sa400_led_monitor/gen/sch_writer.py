"""
Writes a .kicad_sch (format 20230121 = KiCad 7.0, migrates cleanly to 8/9).

Symbols are synthesised rectangles with named pins; every pin carries a net
label at its end, so the schematic is electrically complete and 'Update PCB
from Schematic' reproduces the PCB netlist exactly.  Wires are only drawn
for the LED + resistor chains, which read better as wires.
"""
import uuid
import datetime
from typing import List, Dict, Tuple
import config as C
from design import Footprint

PROJ_UUID = "5a400000-0000-4000-8000-000000000001"
NAMESPACE = uuid.UUID("5a400000-0000-4000-8000-0000000000aa")


def u():
    return str(uuid.uuid4())


def symbol_uuid(ref: str) -> str:
    """Stable per-reference UUID: the PCB footprint's (path ...) points at it, which is how
    KiCad matches a footprint to its symbol in 'Update PCB from Schematic'."""
    return str(uuid.uuid5(NAMESPACE, ref))


def f(x):
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


EFF = '(effects (font (size 1.27 1.27)))'
EFF_H = '(effects (font (size 1.27 1.27)) hide)'


# ---------------------------------------------------------------- symbol library
def box_symbol(name: str, left: List[Tuple[str, str]], right: List[Tuple[str, str]],
               top: List[Tuple[str, str]] = (), bottom: List[Tuple[str, str]] = (),
               ref_prefix="U", footprint="", width=20.32, pin_types=None) -> str:
    pin_types = pin_types or {}
    """Rectangle symbol.  left/right are lists of (number, name) top-to-bottom."""
    n = max(len(left), len(right))
    h = max(n + 1, 3) * 2.54
    hw = width / 2
    hh = h / 2
    lines = [f'    (symbol "sa400:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
             f'      (property "Reference" "{ref_prefix}" (at {f(-hw)} {f(hh + 1.27)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
             f'      (property "Value" "{name}" (at {f(-hw)} {f(-hh - 1.27)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
             f'      (property "Footprint" "{footprint}" (at 0 0 0) {EFF_H})',
             f'      (property "Datasheet" "" (at 0 0 0) {EFF_H})',
             f'      (symbol "{name}_0_1"',
             f'        (rectangle (start {f(-hw)} {f(hh)}) (end {f(hw)} {f(-hh)}) (stroke (width 0.254) (type default)) (fill (type background)))',
             f'      )',
             f'      (symbol "{name}_1_1"']

    def pin(num, nm, x, y, ang, kind="passive"):
        kind = pin_types.get(num, kind)
        return (f'        (pin {kind} line (at {f(x)} {f(y)} {ang}) (length 2.54) '
                f'(name "{nm}" {EFF}) (number "{num}" {EFF}))')
    for i, (num, nm) in enumerate(left):
        y = hh - (i + 1) * 2.54
        lines.append(pin(num, nm, -hw - 2.54, y, 0))
    for i, (num, nm) in enumerate(right):
        y = hh - (i + 1) * 2.54
        lines.append(pin(num, nm, hw + 2.54, y, 180))
    for i, (num, nm) in enumerate(top):
        lines.append(pin(num, nm, (i - (len(top) - 1) / 2) * 2.54, hh + 2.54, 270, "power_in" if nm in ("VCC",) else "passive"))
    for i, (num, nm) in enumerate(bottom):
        lines.append(pin(num, nm, (i - (len(bottom) - 1) / 2) * 2.54, -hh - 2.54, 90, "power_in"))
    lines.append('      )')
    lines.append('    )')
    return "\n".join(lines), {"hw": hw, "hh": hh}


def pin_positions(left, right, top, bottom, hw, hh) -> Dict[str, Tuple[float, float, str]]:
    """pin number -> (dx, dy_up, side) in symbol coords (y up)."""
    pos = {}
    for i, (num, nm) in enumerate(left):
        pos[num] = (-hw - 2.54, hh - (i + 1) * 2.54, "L")
    for i, (num, nm) in enumerate(right):
        pos[num] = (hw + 2.54, hh - (i + 1) * 2.54, "R")
    for i, (num, nm) in enumerate(top):
        pos[num] = ((i - (len(top) - 1) / 2) * 2.54, hh + 2.54, "T")
    for i, (num, nm) in enumerate(bottom):
        pos[num] = ((i - (len(bottom) - 1) / 2) * 2.54, -hh - 2.54, "B")
    return pos


SYMBOLS = {}   # name -> (text, pins dict, footprint)
PIN_NAMES = {}  # lib name -> {pin number: pin name}
REF_LIB = {}    # reference -> lib name (filled by write_sch / placement)


def define(name, left, right, top=(), bottom=(), ref_prefix="U", footprint="", width=20.32, pin_types=None):
    txt, geo = box_symbol(name, left, right, top, bottom, ref_prefix, footprint, width, pin_types)
    SYMBOLS[name] = (txt, pin_positions(left, right, top, bottom, **geo), footprint)
    PIN_NAMES[name] = {num: nm for num, nm in list(left) + list(right) + list(top) + list(bottom)}


def placement():
    """(lib, ref, value, x, y) for every symbol on the sheet - shared by write_sch and nc_nets."""
    out = [("SA400_J1_CardEdge34", "J1", "Shugart 34-pin card edge", 50.8, 80),
           ("MateNLok_4", "J2", "AMP 1-641737-1", 50.8, 170),
           ("74LS14", "U1", "74LS14", 130, 60), ("74LS00", "U2", "74LS00", 200, 60), ("74LS06", "U3", "74LS06", 270, 60)]
    for i in range(5):
        out.append(("R", f"R{9 + i}", "10k", 100 + i * 15.24, 125))
    out += [("C", "C1", "100nF", 130, 150), ("C", "C2", "100nF", 200, 150), ("C", "C3", "100nF", 270, 150)]
    # power section, along the bottom-left of the sheet
    out += [("Polyfuse", "F1", "PTC 0.5A", 80, 175), ("Q_PMOS", "Q1", "IRF4905PBF", 108, 175),
            ("D_Zener", "D11", "1N5339B", 135, 175), ("C", "C6", "100nF", 155, 175), ("CP", "C4", "10uF/16V", 175, 175),
            ("R", "R19", "2k2", 210, 175), ("LED", "D12", "YELLOW", 232, 175),
            ("R", "R21", "470R", 260, 175), ("LED", "D13", "YELLOW", 282, 175)]
    for i, ref in enumerate(["R14", "R15", "R16", "R17", "R18"]):
        out.append(("R", ref, "470R", 100 + i * 15.24, 110))
    for n in range(4):
        y = 195 + n * 18
        out += [("R", f"R{n + 1}", "470R", 200, y), ("LED", f"D{n + 1}", "RED", 230, y),
                ("R", f"R{n + 5}", "470R", 300, y), ("LED", f"D{n + 5}", "GREEN", 330, y)]
    for i in range(4):
        out.append(("MountingHole", f"H{i + 1}", "M3", 360, 195 + i * 15.24))
    snap = lambda v: round(round(v / 1.27) * 1.27, 2)
    return [(lib, ref, val, snap(x), snap(y)) for lib, ref, val, x, y in out]


def nc_nets(net_of_pin: Dict[str, str]) -> Dict[str, str]:
    """KiCad 8+ gives every no-connect pin a net named unconnected-(REF-PINNAME-PadN);
    the PCB pads must carry the same names or DRC parity complains."""
    build_library()
    out = {}
    for lib, ref, *_ in placement():
        for num, nm in PIN_NAMES[lib].items():
            if f"{ref}.{num}" not in net_of_pin:
                out[f"{ref}.{num}"] = f"unconnected-({ref}-{nm}-Pad{num})"
    return out


def build_library():
    define("74LS14", [("1", "1A"), ("3", "2A"), ("5", "3A"), ("9", "4A"), ("11", "5A"), ("13", "6A")],
           [("2", "1Y"), ("4", "2Y"), ("6", "3Y"), ("8", "4Y"), ("10", "5Y"), ("12", "6Y")],
           [("14", "VCC")], [("7", "GND")], footprint="sa400:DIP-14_W7.62mm")
    define("74LS00", [("1", "1A"), ("2", "1B"), ("4", "2A"), ("5", "2B"), ("9", "3A"), ("10", "3B"),
                      ("12", "4A"), ("13", "4B")],
           [("3", "1Y"), ("6", "2Y"), ("8", "3Y"), ("11", "4Y")],
           [("14", "VCC")], [("7", "GND")], footprint="sa400:DIP-14_W7.62mm")
    define("74LS06", [("1", "1A"), ("3", "2A"), ("5", "3A"), ("9", "4A"), ("11", "5A"), ("13", "6A")],
           [("2", "1Y"), ("4", "2Y"), ("6", "3Y"), ("8", "4Y"), ("10", "5Y"), ("12", "6Y")],
           [("14", "VCC")], [("7", "GND")], footprint="sa400:DIP-14_W7.62mm")
    define("LED", [("1", "K")], [("2", "A")], ref_prefix="D", footprint="sa400:LED_D5.0mm", width=7.62)
    define("R", [("1", "1")], [("2", "2")], ref_prefix="R",
           footprint="sa400:R_Axial_DIN0207_P7.62mm_Vertical", width=7.62)
    define("C", [("1", "1")], [("2", "2")], ref_prefix="C",
           footprint="sa400:C_Disc_D5.0mm_P2.50mm", width=7.62)
    define("CP", [("1", "+")], [("2", "-")], ref_prefix="C",
           footprint="sa400:CP_Radial_D5.0mm_P2.50mm", width=7.62)
    even = [(str(p), n) for p, n in [(2, "spare"), (4, "spare"), (6, "DS4#"), (8, "INDEX#"), (10, "DS1#"),
                                      (12, "DS2#"), (14, "DS3#"), (16, "MOTOR_ON#"), (18, "DIR#"),
                                      (20, "STEP#"), (22, "WDATA#"), (24, "WGATE#"), (26, "TRK00#"),
                                      (28, "WPROT#"), (30, "RDATA#"), (32, "spare"), (34, "spare")]
            if p not in C.J1_DROP_PADS]
    odd = [(str(p), "GND") for p in range(1, 35, 2) if p not in C.J1_DROP_PADS]
    define("SA400_J1_CardEdge34", even, odd, ref_prefix="J", footprint="sa400:CardEdge_34_SA400", width=30.48)
    define("MateNLok_4", [("1", "+12V"), ("2", "+12V_RTN"), ("3", "+5V_RTN"), ("4", "+5V")], [],
           ref_prefix="J", footprint="sa400:MateNLok_4_RA", width=15.24,
           pin_types={"1": "power_out", "2": "power_out", "3": "passive", "4": "power_out"})   # both returns land on GND; only one may be a power output for ERC
    define("MountingHole", [], [], ref_prefix="H", footprint="sa400:MountingHole_3.2mm_M3", width=7.62)
    define("D_Schottky", [("1", "K")], [("2", "A")], ref_prefix="D", footprint="sa400:D_DO-41_P7.62mm_Horizontal", width=7.62)
    define("D_TVS", [("1", "K")], [("2", "A")], ref_prefix="D", footprint="sa400:D_DO-15_P10.16mm_Vertical", width=7.62)
    define("D_Zener", [("1", "K")], [("2", "A")], ref_prefix="D", footprint="sa400:D_DO-15_P10.16mm_Vertical", width=7.62)
    define("Polyfuse", [("1", "1")], [("2", "2")], ref_prefix="F", footprint="sa400:Fuse_Radial_P5.08mm", width=7.62)
    define("Q_PMOS", [("1", "G")], [("3", "S")], top=[("2", "D")], ref_prefix="Q",
           footprint="sa400:TO-220-3_Vertical", width=12.7, pin_types={"3": "power_out"})   # source feeds the +5V rail


# ---------------------------------------------------------------- schematic
def sym_instance(lib: str, ref: str, value: str, x: float, y: float, net_of_pin: Dict[str, str],
                 extra_props: Dict[str, str] = None) -> Tuple[str, List[str]]:
    """Return (symbol s-expr, list of label/no_connect s-exprs)."""
    txt, pins, footprint = SYMBOLS[lib]
    lines = [f'  (symbol (lib_id "sa400:{lib}") (at {f(x)} {f(y)} 0) (unit 1) (in_bom yes) (on_board yes) '
             f'(uuid {symbol_uuid(ref)})',
             f'    (property "Reference" "{ref}" (at {f(x - 8)} {f(y - 2)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
             f'    (property "Value" "{value}" (at {f(x - 8)} {f(y)} 0) (effects (font (size 1.27 1.27)) (justify left)))',
             f'    (property "Footprint" "{footprint}" (at {f(x)} {f(y)} 0) {EFF_H})',
             f'    (property "Datasheet" "" (at {f(x)} {f(y)} 0) {EFF_H})']
    for k, v in (extra_props or {}).items():
        lines.append(f'    (property "{k}" "{v}" (at {f(x)} {f(y)} 0) {EFF_H})')
    labels = []
    for num, (dx, dy, side) in pins.items():
        lines.append(f'    (pin "{num}" (uuid {u()}))')
        px, py = x + dx, y - dy   # schematic y is down
        net = net_of_pin.get(f"{ref}.{num}")
        if net is None:
            labels.append(f'  (no_connect (at {f(px)} {f(py)}) (uuid {u()}))')
            continue
        ang = {"L": 180, "R": 0, "T": 90, "B": 270}[side]
        labels.append(f'  (global_label "{net}" (shape passive) (at {f(px)} {f(py)} {ang}) (fields_autoplaced) '
                      f'(effects (font (size 1.27 1.27)) (justify {"right" if side == "L" else "left"})) (uuid {u()})'
                      f' (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {f(px)} {f(py)} 0) {EFF_H}))')
    lines.append(f'    (instances (project "{C.PROJECT}" (path "/{PROJ_UUID}" (reference "{ref}") (unit 1))))')
    lines.append('  )')
    return "\n".join(lines), labels


def text(x, y, s, size=1.5):
    s = s.replace('"', "'").replace("\n", "\\n")
    return f'  (text "{s}" (at {f(x)} {f(y)} 0) (effects (font (size {f(size)} {f(size)})) (justify left bottom)) (uuid {u()}))'


def write_symbol_lib(path: str):
    """sa400.kicad_sym: the same symbols the schematic embeds, so ERC finds the library."""
    build_library()
    out = ['(kicad_symbol_lib (version 20231120) (generator sa400_gen)']
    for name, (txt, _, _) in SYMBOLS.items():
        out.append(txt.replace(f'(symbol "sa400:{name}"', f'(symbol "{name}"'))
    out.append(')')
    open(path, "w").write("\n".join(out) + "\n")


def write_sch(path: str, fps: List[Footprint], net_of_pin: Dict[str, str], version: str):
    build_library()
    today = datetime.date.today().isoformat()
    out = ['(kicad_sch (version 20230121) (generator eeschema)', f'  (uuid {PROJ_UUID})', '  (paper "A3")',
           f'  (title_block (title "{C.TITLE}") (date "{today}") (rev "v{version}") (company "Ven") '
           f'(comment 1 "RED_n = DSn active.  GREEN_n = DSn AND WRITE GATE.  All bus signals active-low.") '
           f'(comment 2 "Generated by gen/build.py") )',
           '  (lib_symbols']
    for name, (txt, _, _) in SYMBOLS.items():
        out.append(txt)
    out.append('  )')
    body, labels = [], []

    def place(lib, ref, value, x, y, extra=None):
        s, l = sym_instance(lib, ref, value, x, y, net_of_pin, extra)
        body.append(s)
        labels.extend(l)

    by_ref = {fp.ref: fp for fp in fps}
    # --- sheet 1 layout (A3 = 420 x 297 mm)
    for lib, ref, value, x, y in placement():
        place(lib, ref, value, x, y)

    out += body
    out += labels
    out.append(text(20, 20, f"{C.PROJECT}  v{version}  -  {C.TITLE}", 3.0))
    out.append(text(20, 28, "Shugart bus signals are active-low, open-collector, terminated (150R) at the LAST DRIVE. "
                            "This board is a high-impedance tap: 74LS14 inputs plus 10k pull-ups only.", 1.5))
    out.append(text(20, 33, "U1 74LS14 inverts the bus: DSn and WG are HIGH when the line is asserted.  "
                            "U3 74LS06 (open collector) sinks the RED LED when DSn is high.  "
                            "U2 74LS00 sinks the GREEN LED when DSn AND WG are both high.", 1.5))
    out.append(text(20, 38, "LED current = (5 - 0.4 - Vf) / 470R  ~ 5.5 mA with a 2.0 V standard LED (within the 74LS00 8 mA sink).  "
                            "High-efficiency LEDs: use 1k5 (~1.8 mA).", 1.5))
    out.append(text(20, 43, "Power (as the SA400): J2-4 +5 V -> F1 PTC -> Q1 P-MOSFET reverse switch -> +5V [D11 5.6 V clamp, C6, C4] -> logic. "
                            "J2-1 +12 V lights D12 only (R19 2k2, ~4.5 mA).  D13 shows the +5 V rail.  Bus lines pass through 470R (R14-R18) before the pull-ups and 74LS14.", 1.5))
    out.append(text(20, 48, "Unused gate inputs tied to GND; unused outputs left open.  Net names: XXX_n = bus finger (active-low), XXX_in = after the series resistor, XXX = inverted.", 1.5))
    out.append(text(190, 190, "LED chains: +5V - R - LED anode ; LED cathode - gate output (sinks when active)", 1.5))
    out.append(f'  (sheet_instances (path "/" (page "1")))')
    out.append(')')
    open(path, "w").write("\n".join(out) + "\n")
