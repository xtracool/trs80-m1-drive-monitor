"""
Component placement and netlist for the SA400 LED monitor.

Coordinate system (KiCad board coordinates, mm):
  origin  = top-left corner of the board outline
  +x      = to the right
  +y      = DOWN the page
  y = 0   = the rear edge: the card-edge fingers (J1) and the power
            connector (J2) are on this edge, fingers pointing up/away.

Viewed from the component side with the card edge pointing away, J1 pin 2
is at the RIGHT (established in the extender / activity-monitor projects
from the SA400L manual section 3.2 and a physical drive).

Everything is placed on a 1.27 mm (0.050 in) grid so the maze router can
reach every pad.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import config as C

G = C.GRID


def g(n: int) -> float:
    """n grid units -> mm."""
    return round(n * G, 3)


# ---------------------------------------------------------------- data model
@dataclass
class Pad:
    number: str
    x: float                       # absolute board coords
    y: float
    shape: str                     # "circle" | "rect" | "oval"
    size: Tuple[float, float]
    drill: Optional[float]         # None for SMD / edge pads
    layers: Tuple[str, ...]
    net: Optional[str]             # None = unconnected


@dataclass
class Footprint:
    ref: str
    value: str
    lib_name: str                  # e.g. "sa400:LED_D5.0mm"
    x: float
    y: float
    rot: float = 0.0
    layer: str = "F.Cu"
    pads: List[Pad] = field(default_factory=list)
    silk: List[tuple] = field(default_factory=list)   # ("line",x1,y1,x2,y2) / ("circle",cx,cy,r) / ("text",x,y,s,size)
    fab: List[tuple] = field(default_factory=list)
    courtyard: Optional[Tuple[float, float, float, float]] = None  # x1,y1,x2,y2 absolute
    description: str = ""
    lcsc: str = ""
    ref_rot: float = 0.0
    ref_pos: Optional[Tuple[float, float, float]] = None   # (dx, dy, rot) override, relative to the footprint origin


# ---------------------------------------------------------------- footprint builders
def dip14(ref, value, x0, y0, desc, lcsc="") -> Footprint:
    """DIP-14, 300 mil.  Pin 1 at (x0, y0), pins 1-7 run +x, pins 8-14 run -x
    on the row 7.62 mm ABOVE (smaller y).  Notch on the left."""
    fp = Footprint(ref, value, "sa400:DIP-14_W7.62mm", x0 + 3 * 2.54, y0 - 3.81,
                   description=desc, lcsc=lcsc)
    for i in range(7):
        fp.pads.append(Pad(str(i + 1), x0 + i * 2.54, y0, "circle" if i else "rect",
                           (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))
        fp.pads.append(Pad(str(14 - i), x0 + i * 2.54, y0 - 7.62, "circle",
                           (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))
    # body outline on silk (6.35 mm wide body), notch at left
    bx1, bx2 = x0 - 1.27, x0 + 6 * 2.54 + 1.27
    by1, by2 = y0 - 7.62 + 1.27, y0 - 1.27
    fp.silk += [("line", bx1, by1, bx2, by1), ("line", bx1, by2, bx2, by2),
                ("line", bx2, by1, bx2, by2),
                ("line", bx1, by1, bx1, by1 + 1.5), ("line", bx1, by2, bx1, by2 - 1.5),
                ("arc", bx1, (by1 + by2) / 2, 1.5)]
    fp.fab += [("rect", bx1, by1, bx2, by2)]
    fp.courtyard = (x0 - 1.27 - 0.25, y0 - 7.62 - 1.0 - 0.25, bx2 + 0.25, y0 + 1.0 + 0.25)
    return fp


def resistor(ref, value, x, y_top, desc, lcsc="") -> Footprint:
    """Axial 1/4 W, vertical, 7.62 mm pitch.  Pin 1 at (x, y_top), pin 2 below."""
    fp = Footprint(ref, value, "sa400:R_Axial_DIN0207_P7.62mm_Vertical",
                   x, y_top, description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x, y_top, "circle", (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", x, y_top + 7.62, "circle", (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))
    fp.silk += [("circle", x, y_top, 1.5), ("line", x, y_top + 1.5, x, y_top + 7.62 - 1.2)]
    fp.courtyard = (x - 1.5, y_top - 1.5, x + 1.5, y_top + 7.62 + 1.25)
    return fp


def led5(ref, value, xc, y, desc, lcsc="") -> Footprint:
    """5 mm LED, leads horizontal at 2.54 pitch.  Pin 1 = cathode (K, flat side)
    at (xc-1.27, y), pin 2 = anode at (xc+1.27, y)."""
    fp = Footprint(ref, value, "sa400:LED_D5.0mm", xc, y, description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", xc - 1.27, y, "rect", (1.8, 1.8), 0.9, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", xc + 1.27, y, "circle", (1.8, 1.8), 0.9, ("*.Cu", "*.Mask"), None))
    fp.silk += [("circle", xc, y, 2.6), ("line", xc - 2.6, y - 1.8, xc - 2.6, y + 1.8)]
    fp.courtyard = (xc - 3.1, y - 3.1, xc + 3.1, y + 3.1)
    return fp


def cap_100n(ref, x, y_top, desc, lcsc="") -> Footprint:
    fp = Footprint(ref, "100nF", "sa400:C_Disc_D5.0mm_P2.50mm", x, y_top + 1.27,
                   description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x, y_top, "circle", (1.5, 1.5), 0.8, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", x, y_top + 2.54, "circle", (1.5, 1.5), 0.8, ("*.Cu", "*.Mask"), None))
    # body outline as two side lines so the silk never crosses the pads
    fp.silk += [("line", x - 2.5, y_top - 1.3, x - 2.5, y_top + 3.84), ("line", x + 2.5, y_top - 1.3, x + 2.5, y_top + 3.84),
                ("line", x - 2.5, y_top - 1.3, x - 1.2, y_top - 1.3), ("line", x + 1.2, y_top - 1.3, x + 2.5, y_top - 1.3),
                ("line", x - 2.5, y_top + 3.84, x - 1.2, y_top + 3.84), ("line", x + 1.2, y_top + 3.84, x + 2.5, y_top + 3.84)]
    fp.courtyard = (x - 2.8, y_top - 1.6, x + 2.8, y_top + 4.1)
    return fp


def cap_10u(ref, x, y_top, desc, lcsc="", value="10uF/16V") -> Footprint:
    fp = Footprint(ref, value, "sa400:CP_Radial_D5.0mm_P2.50mm", x, y_top + 1.27,
                   description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x, y_top, "rect", (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))  # +
    fp.pads.append(Pad("2", x, y_top + 2.54, "circle", (1.6, 1.6), 0.8, ("*.Cu", "*.Mask"), None))
    fp.silk += [("circle", x, y_top + 1.27, 2.6), ("text", x + 2.2, y_top - 2.4, "+", 0.8)]
    fp.courtyard = (x - 3.0, y_top - 1.8, x + 3.0, y_top + 2.54 + 1.8)
    return fp


def diode_axial(ref, value, x, y_k, pitch, desc, body_d=2.7, lcsc="") -> Footprint:
    """Axial diode, vertical, pin 1 = cathode (band) at (x, y_k), pin 2 = anode at (x, y_k + pitch)."""
    name = "D_DO-41_P7.62mm_Vertical" if pitch < 9 else "D_DO-15_P10.16mm_Vertical"
    fp = Footprint(ref, value, f"sa400:{name}", x, y_k + pitch / 2, description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x, y_k, "rect", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", x, y_k + pitch, "circle", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    r = body_d / 2 + 0.3
    fp.silk += [("circle", x, y_k, r), ("line", x, y_k + r, x, y_k + pitch - 1.3),
                ("line", x - r, y_k - r, x + r, y_k - r)]      # band mark on the cathode end
    fp.courtyard = (x - r - 0.3, y_k - r - 0.4, x + r + 0.3, y_k + pitch + 1.3)
    return fp


def diode_axial_h(ref, value, x_a, x_k, y, desc, lcsc="") -> Footprint:
    """Axial DO-41, horizontal: pin 1 = cathode (band) at (x_k, y), pin 2 = anode at (x_a, y)."""
    fp = Footprint(ref, value, "sa400:D_DO-41_P7.62mm_Horizontal", (x_a + x_k) / 2, y, description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x_k, y, "rect", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", x_a, y, "circle", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    xl, xr = min(x_a, x_k), max(x_a, x_k)
    band = x_k - 0.6 if x_k > x_a else x_k + 0.6
    fp.silk += [("rect", xl + 1.6, y - 1.4, xr - 1.6, y + 1.4),
                ("line", band - (1.6 if x_k > x_a else -1.6) * 0 + (-1.0 if x_k > x_a else 1.0), y - 1.4,
                 band - (1.6 if x_k > x_a else -1.6) * 0 + (-1.0 if x_k > x_a else 1.0), y + 1.4)]   # band at the cathode end
    fp.courtyard = (xl - 1.3, y - 1.9, xr + 1.3, y + 1.9)
    return fp


def fuse_radial(ref, value, x1, y, desc, lcsc="") -> Footprint:
    """Radial PTC / polyfuse, 5.08 mm pitch, horizontal."""
    fp = Footprint(ref, value, "sa400:Fuse_Radial_P5.08mm", x1 + 2.54, y, description=desc, lcsc=lcsc)
    fp.pads.append(Pad("1", x1, y, "rect", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    fp.pads.append(Pad("2", x1 + 5.08, y, "circle", (1.8, 1.8), 1.0, ("*.Cu", "*.Mask"), None))
    fp.silk += [("rect", x1 - 1.9, y - 2.3, x1 + 5.08 + 1.9, y + 2.3)]
    fp.courtyard = (x1 - 2.3, y - 2.7, x1 + 5.08 + 2.3, y + 2.7)
    return fp


def to220_vertical(ref, value, x1, y, desc, lcsc="") -> Footprint:
    """TO-220AB standing up, pins 1-2-3 at 2.54 mm along +x (pin 1 = square pad, leftmost).

    Geometry follows KiCad's `TO-220-3_Vertical` (Vishay TO-220 drawing 66542): with pin 1 at -x the
    plastic label face looks toward +y and the metal tab is at -y, so the 4.4 mm body straddles the pin
    row from y-3.15 (tab back) to y+1.25 (face).  Silk: body outline, a line marking the tab, and G/D/S
    pin labels under the pads.  (v0.2.2 drew the box on the +y side, which JLCPCB queried on 2026-10-07.)
    """
    fp = Footprint(ref, value, "sa400:TO-220-3_Vertical", x1 + 2.54, y, description=desc, lcsc=lcsc)
    for i in range(3):
        fp.pads.append(Pad(str(i + 1), x1 + i * 2.54, y, "rect" if i == 0 else "oval", (1.8, 2.4), 1.0,
                           ("*.Cu", "*.Mask"), None))
    xl, xr = x1 - 2.58, x1 + 5.08 + 2.58                                   # 10.24 mm wide outline
    fp.silk += [("rect", xl, y - 3.27, xr, y + 1.65),                       # body, 0.45 mm clear of the pads
                ("line", xl, y - 1.76, xr, y - 1.76),                       # plastic / metal-tab boundary
                ("text", x1 + 2.54, y - 2.5, "TAB", 0.8),
                ("text", x1, y + 2.4, "G", 0.8), ("text", x1 + 2.54, y + 2.4, "D", 0.8),
                ("text", x1 + 5.08, y + 2.4, "S", 0.8)]
    fp.fab += [("rect", x1 - 2.46, y - 3.15, x1 + 5.08 + 2.46, y + 1.25)]
    fp.courtyard = (x1 - 2.71, y - 3.4, x1 + 5.08 + 2.71, y + 1.9)
    return fp


def mounting_hole(ref, x, y) -> Footprint:
    fp = Footprint(ref, "M3", "sa400:MountingHole_3.2mm_M3", x, y,
                   description="Mounting hole, M3 / #4-40 clearance, non-plated")
    fp.pads.append(Pad("", x, y, "circle", (C.MOUNT_HOLE_DRILL, C.MOUNT_HOLE_DRILL),
                       C.MOUNT_HOLE_DRILL, ("*.Cu", "*.Mask"), None))
    fp.silk += [("circle", x, y, C.MOUNT_HOLE_PAD / 2 + 0.3)]
    fp.courtyard = (x - 3.5, y - 3.5, x + 3.5, y + 3.5)
    return fp


def card_edge() -> Footprint:
    """J1: 34-contact card edge on the rear (y=0) board edge.
    Even pins on F.Cu, odd pins on B.Cu, pin 2 nearest the right corner."""
    x2 = C.J1_TAB_RIGHT - C.J1_PIN2_FROM_RIGHT_EDGE
    fp = Footprint("J1", "Shugart 34-pin card edge", "sa400:CardEdge_34_SA400",
                   x2 - 8 * C.J1_PITCH, C.J1_FINGER_LEN / 2,
                   description="34-contact 0.100 in card edge per 3M TS-0010-14 recommended PCB layout / SA400L fig 3-2")
    for i in range(17):
        even = 2 + 2 * i
        odd = 1 + 2 * i
        x = x2 - i * C.J1_PITCH
        for pin, layer in ((even, "F"), (odd, "B")):
            if pin in C.J1_DROP_PADS:
                continue
            w = C.J1_NARROW_PADS.get(pin, C.J1_FINGER_W)
            fp.pads.append(Pad(str(pin), x, (C.J1_FINGER_LEN + C.J1_FINGER_SETBACK) / 2, "rect",
                               (w, C.J1_FINGER_LEN - C.J1_FINGER_SETBACK), None,
                               (layer + ".Cu", layer + ".Mask"), None))
        fp.silk.append(("text", x, C.J1_FINGER_DEPTH + 2.2, str(even), 0.8))
    if C.J1_POST_HOLES:
        for x in (x2, x2 - 16 * C.J1_PITCH):
            fp.pads.append(Pad("", x, C.J1_POST_HOLE_Y, "circle", (C.J1_POST_HOLE_DIA,) * 2,
                               C.J1_POST_HOLE_DIA, ("*.Cu", "*.Mask"), None))
    fp.courtyard = (tab_left(), 0, C.J1_TAB_RIGHT, C.J1_FINGER_DEPTH + 0.5)
    return fp


def tab_left() -> float:
    """x of the left shoulder of the card-edge tab (pin-34 side)."""
    return C.J1_TAB_RIGHT - C.J1_TAB_W


def key_slot_x() -> float:
    a, b = C.J1_KEY_BETWEEN
    x2 = C.J1_TAB_RIGHT - C.J1_PIN2_FROM_RIGHT_EDGE
    xa = x2 - ((a - 2) // 2) * C.J1_PITCH
    xb = x2 - ((b - 2) // 2) * C.J1_PITCH
    return (xa + xb) / 2


def j2_pin_x(i: int) -> float:
    """x of J2 pin i (0-based) - direction set by config so the pin-1 end can be flipped."""
    return C.J2_PIN1_X + C.J2_PIN_DIR * i * C.J2_PITCH


def mate_n_lok() -> Footprint:
    """J2: Commercial MATE-N-LOK 4-position right-angle header on the COMPONENT side, mating face at
    the recessed rear edge (v0.2.4).  Pads suit TE 1-641737-1 (right angle) and 350211-1 (vertical)."""
    xs = [j2_pin_x(i) for i in range(4)]
    fp = Footprint("J2", "AMP 1-641737-1", "sa400:MateNLok_4_RA",
                   (xs[0] + xs[3]) / 2, C.J2_ROW_Y, layer=C.J2_LAYER,
                   description="TE Commercial Mate-N-Lok 4-pos right-angle PCB header 1-641737-1 "
                               "(or vertical 350211-1), component side, SA400 pinout")
    for i, x in enumerate(xs):
        fp.pads.append(Pad(str(i + 1), x, C.J2_ROW_Y, "rect" if i == 0 else "circle",
                           (C.J2_PAD, C.J2_PAD), C.J2_DRILL, ("*.Cu", "*.Mask"), None))
    xl, xr = min(xs) - 4.0, max(xs) + 4.0
    yt = C.J1_REAR_RECESS + 0.5          # housing face sits at the recessed rear edge
    fp.silk += [("rect", xl, yt, xr, C.J2_ROW_Y + 4.0),                      # right-angle housing
                ("line", xl, yt + 1.0, xr, yt + 1.0)]                        # mating face / plug entry
    # labels below the housing so they stay readable with the header fitted
    for i, nm in enumerate(["+12V", "RTN", "RTN", "+5V"]):
        fp.silk.append(("text", xs[i], C.J2_ROW_Y + 6.0, f"{i + 1} {nm}", 0.8))        # fp_text is centred
    fp.silk.append(("text", (xl + xr) / 2 + 2.0, C.J2_ROW_Y + 7.9, "J2 PWR IN - SA400 pinout", 0.8))   # short: clears H1 silk
    fp.fab += [("rect", xl, yt, xr, C.J2_ROW_Y + 4.0)]
    fp.courtyard = (xl - 0.5, yt - 0.3, xr + 0.5, C.J2_ROW_Y + 4.5)
    fp.ref_pos = (xr + 1.6 - fp.x, 0.0, 90)      # "J2" beside the housing: above it is the recess (off-board)
    return fp


# ---------------------------------------------------------------- placement
def build() -> Tuple[List[Footprint], Dict[str, str]]:
    """Return (footprints, net_of_pin) where net_of_pin maps 'REF.pin' -> net."""
    fps: List[Footprint] = []

    # --- connectors
    j1 = card_edge()
    fps.append(j1)
    fps.append(mate_n_lok())

    # --- logic: U1 receivers near the fingers, U2/U3 drivers between U1 and the LEDs
    fps.append(dip14("U1", "74LS14", g(80), g(29), "Hex Schmitt inverter - bus receivers"))
    fps.append(dip14("U2", "74LS00", g(35), g(60), "Quad NAND - GREEN = DSn AND WG"))
    fps.append(dip14("U3", "74LS06", g(80), g(60), "Hex OC inverter - RED = DSn"))

    # --- decoupling
    fps.append(cap_100n("C1", g(96), g(24), "Decoupling U1"))
    fps.append(cap_100n("C2", g(51), g(57), "Decoupling U2"))
    fps.append(cap_100n("C3", g(96), g(57), "Decoupling U3"))
    # --- +5 V from the PSU (as the SA400 does): F1 PTC -> Q1 P-MOSFET reverse switch -> +5V rail
    #     (D11 5.6 V clamp, C6 100 nF, C4 10 uF).  +12 V pin drives a "12 V present" indicator only.
    PY = g(26)   # power row: 33.02 (was 30.48 up to 0.2.3; moved for the component-side J2 labels)
    fps.append(fuse_radial("F1", "PTC 0.5A", g(11), PY, "Resettable fuse on the +5 V input"))
    fps.append(to220_vertical("Q1", "IRF4905PBF", g(20), PY, "P-MOSFET reverse-polarity switch (G-D-S)"))
    fps.append(diode_axial("D11", "1N5339B", g(29), PY, 10.16, "5.6 V clamp on the +5 V rail"))
    fps.append(cap_100n("C6", g(33), PY, "Rail 100nF at the input"))
    fps.append(cap_10u("C4", g(38), PY, "Bulk decoupling on +5 V"))
    fps.append(resistor("R19", "2k2", g(43), PY, "+12 V indicator series"))
    fps.append(led5("D12", "YELLOW", g(47), PY, "+12 V present"))
    fps.append(resistor("R21", "470R", g(52), PY, "+5 V indicator series"))
    fps.append(led5("D13", "YELLOW", g(56), PY, "+5 V present"))
    # --- series resistors between the fingers and the receiver nodes
    for ref, x in (("R14", g(82)), ("R15", g(88)), ("R16", g(92)), ("R17", g(96)), ("R18", g(100))):
        fps.append(resistor(ref, "470R", x, g(14), "Bus series / fault-limiting resistor"))

    # --- bus pull-ups (keep LS14 inputs defined with no cable attached)
    pull_x = [g(77), g(73), g(69), g(65), g(61)]      # 5.08 mm centres: courtyards clear
    for i, x in enumerate(pull_x):
        rp = resistor(f"R{9 + i}", "10k", x, g(15), "Bus pull-up")
        rp.ref_rot = 90                      # refs stacked at 5.08 mm; rotated to stay clear of J1's pin numbers
        fps.append(rp)

    # --- LEDs along the front edge, one red/green pair per drive
    red_x = [g(24), g(44), g(64), g(84)]
    for n in range(4):
        xr = red_x[n]
        xg = xr + 6 * G                                # 7.62 mm: 5 mm LED courtyards clear
        fps.append(led5(f"D{n + 1}", "RED", xr, g(93), f"Drive {n + 1} selected"))
        fps.append(led5(f"D{n + 5}", "GREEN", xg, g(93), f"Drive {n + 1} write gate"))
        fps.append(resistor(f"R{n + 1}", "470R", xr + 1.27, g(79), f"Red LED {n + 1} series"))
        fps.append(resistor(f"R{n + 5}", "470R", xg + 1.27, g(79), f"Green LED {n + 1} series"))

    # --- mounting
    for i, (x, y) in enumerate(C.MOUNT_HOLES):
        fps.append(mounting_hole(f"H{i + 1}", x, y))

    # ---------------------------------------------------------------- nets
    net: Dict[str, str] = {}

    def N(ref_pin, name):
        net[ref_pin] = name

    # J1 - Shugart bus.  Odd pins are ground.  Even pins other than the five
    # we monitor are left UNCONNECTED so the board is a pure high-impedance tap.
    for pin in range(1, 35, 2):
        if pin in C.J1_DROP_PADS or (C.J1_POST_HOLES and pin in (1, 33)):
            continue            # pins 1/33 sit over the post holes; 15 other GND fingers remain
        N(f"J1.{pin}", "GND")
    N("J1.10", "DS1_n"); N("J1.12", "DS2_n"); N("J1.14", "DS3_n"); N("J1.6", "DS4_n")
    N("J1.24", "WG_n")
    # series resistors: finger net -> R -> receiver node (_in)
    for ref, sig in (("R18", "DS4"), ("R17", "DS1"), ("R16", "DS2"), ("R15", "DS3"), ("R14", "WG")):
        N(f"{ref}.1", f"{sig}_n"); N(f"{ref}.2", f"{sig}_in")

    # J2 - +5 V powers the logic (as on the SA400); +12 V only lights an indicator; both returns to GND.
    N("J2.4", "+5V_IN"); N("J2.1", "+12V_IN"); N("J2.2", "GND"); N("J2.3", "GND")
    N("F1.1", "+5V_IN"); N("F1.2", "+5V_F")
    N("Q1.2", "+5V_F"); N("Q1.3", "+5V"); N("Q1.1", "GND")   # drain from the fuse, source = rail, gate to GND
    N("D11.1", "+5V"); N("D11.2", "GND")                     # zener cathode on +5 V
    N("C6.1", "+5V"); N("C6.2", "GND")
    N("R19.1", "+12V_IN"); N("R19.2", "LED12"); N("D12.2", "LED12"); N("D12.1", "GND")
    N("R21.1", "+5V"); N("R21.2", "LED5"); N("D13.2", "LED5"); N("D13.1", "GND")

    # U1 74LS14: in 1->out 2, 3->4, 5->6, 9->8, 11->10, 13->12
    N("U1.1", "DS1_in"); N("U1.2", "DS1")
    N("U1.3", "DS2_in"); N("U1.4", "DS2")
    N("U1.5", "DS3_in"); N("U1.6", "DS3")
    N("U1.9", "DS4_in"); N("U1.8", "DS4")
    N("U1.11", "WG_in"); N("U1.10", "WG")
    N("U1.13", "GND")            # unused gate input tied low; output 12 left open
    N("U1.14", "+5V"); N("U1.7", "GND")

    # U2 74LS00: (1,2)->3 (4,5)->6 (9,10)->8 (12,13)->11
    N("U2.1", "DS1"); N("U2.2", "WG"); N("U2.3", "GRN1_K")
    N("U2.4", "DS2"); N("U2.5", "WG"); N("U2.6", "GRN2_K")
    N("U2.9", "DS3"); N("U2.10", "WG"); N("U2.8", "GRN3_K")
    N("U2.12", "DS4"); N("U2.13", "WG"); N("U2.11", "GRN4_K")
    N("U2.14", "+5V"); N("U2.7", "GND")

    # U3 74LS06: 1->2, 3->4, 5->6, 9->8, 11->10, 13->12 (open collector)
    N("U3.1", "DS1"); N("U3.2", "RED1_K")
    N("U3.3", "DS2"); N("U3.4", "RED2_K")
    N("U3.5", "DS3"); N("U3.6", "RED3_K")
    N("U3.9", "DS4"); N("U3.8", "RED4_K")
    N("U3.11", "GND"); N("U3.13", "GND")   # unused inputs tied low, OC outputs open
    N("U3.14", "+5V"); N("U3.7", "GND")

    # LEDs and series resistors
    for n in range(1, 5):
        N(f"D{n}.1", f"RED{n}_K"); N(f"D{n}.2", f"RED{n}_A")
        N(f"R{n}.1", "+5V"); N(f"R{n}.2", f"RED{n}_A")
        N(f"D{n + 4}.1", f"GRN{n}_K"); N(f"D{n + 4}.2", f"GRN{n}_A")
        N(f"R{n + 4}.1", "+5V"); N(f"R{n + 4}.2", f"GRN{n}_A")

    # pull-ups
    for i, sig in enumerate(["DS1_in", "DS2_in", "DS3_in", "DS4_in", "WG_in"]):
        N(f"R{9 + i}.1", "+5V"); N(f"R{9 + i}.2", sig)

    # decoupling
    for c in ("C1", "C2", "C3", "C4"):
        N(f"{c}.1", "+5V"); N(f"{c}.2", "GND")

    # apply
    for fp in fps:
        for p in fp.pads:
            key = f"{fp.ref}.{p.number}"
            p.net = net.get(key)
    return fps, net


def net_names(fps: List[Footprint]) -> List[str]:
    names = sorted({p.net for fp in fps for p in fp.pads if p.net})
    # KiCad convention: net 0 is the unconnected net; put GND/+5V first for readability
    ordered = [n for n in ("GND", "+5V") if n in names] + [n for n in names if n not in ("GND", "+5V")]
    return ordered
