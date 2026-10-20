"""
Design configuration for the SA400 form-factor LED monitor board.

Every dimension is in millimetres unless the name says otherwise.
Every value that came from a document has its source in the comment.
Anything marked ASSUMED is a design decision that must be verified
against hardware before ordering (see docs/MECHANICAL.md).
"""

VERSION = "0.2.4"
PROJECT = "sa400_led_monitor"
TITLE = "SA400 form-factor drive-select / write-gate LED monitor"

IN = 25.4

# ---------------------------------------------------------------- board
BOARD_W = 5.5 * IN          # 139.70  user spec: 5.5 in edge carries J1 and J2
BOARD_H = 5.0 * IN          # 127.00  user spec: 5.0 in (5.5 in is also acceptable)
BOARD_THICKNESS = 1.6       # SA400L OEM manual fig 3-2: 0.062 +/- 0.007 in

# ---------------------------------------------------------------- J1 card edge
# SA400L OEM manual (P/N 39019-1) section 3.2 and figure 3-2
J1_PITCH = 0.100 * IN       # 2.54   contact pitch
# 3M TS-0010-14 sheet 3 "Recommended PCB Layout" for the 3463 (34-way) connector is THE standard
# for this edge; Shugart fig 3-2 copies it.  https://multimedia.3m.com/mws/media/22013O/3m-tm-100-in-card-edge-connector-w-o-mounting-flng-ts0010.pdf
J1_FINGER_W = 0.055 * IN    # 1.40   3M: contact width .055 +/- .005
J1_FINGER_LEN = 0.400 * IN  # 10.16  3M: contact reach .400 +/- .015 from the insertion edge
J1_FINGER_SETBACK = 0.66    # 3M ".026 [0.66]" copper setback from the edge; JLCPCB needs >= 0.6 for the bevel
J1_FINGER_DEPTH = 0.450 * IN  # 11.43 3M: tab depth .450 MIN (Shugart fig 3-2 0.450)
J1_TAB_W = 1.795 * IN       # 45.59  3M dimension A (+/- .005) = Shugart fig 3-2 1.795
J1_TAB_MARGIN = (J1_TAB_W - 16 * J1_PITCH - J1_FINGER_W) / 2   # 1.775 bare board beyond pins 2 and 34
J1_PIN2_FROM_RIGHT_EDGE = J1_TAB_W / 2 - 8 * J1_PITCH       # 2.475: pin 2 centre to tab edge
# TEAC FD-55 spec fig 103 shows the same construction: fingers on a 45.44 mm tab, key slot 0.91.
# PHOTO of a real SA400 PCB (P/N 25080, supplied by Ven, 2026-09-05): the tab PROTRUDES from the
# rear edge - the whole rear edge is set back by the tab depth on both sides, the tab sits about
# 5 mm from the pin-2 corner, two small holes sit at the tab root in line with pins 2 and 34,
# and that particular board has NO key slot cut (keying is "optional" per the OEM manual).
J1_REAR_RECESS = J1_FINGER_DEPTH   # 11.43  rear edge set back by the tab depth (photo)
J1_TAB_CORNER_GAP = 5.08    # ASSUMED +/-1.5: pin-2 side shoulder to the board corner, scaled from the photo
J1_TAB_RIGHT = BOARD_W - J1_TAB_CORNER_GAP
J1_KEY_SLOT = True          # key slot between pins 4 and 6 (photo + OEM manual sec 3.2)
J1_POST_HOLES = True        # 2 x 1.6 mm holes at the tab root in line with pins 2 and 34 (photo, fig 3-2 "0.063 NOM (2X)")
J1_POST_HOLE_DIA = 1.6
J1_TAB_CORNER_R = 1.02      # 3M: R.040
J1_POST_HOLE_Y = J1_FINGER_DEPTH   # 11.43: hole centred on the tab-root line, ring touching the finger end (photo, scaled off the 2.54 pitch)
J1_KEY_SLOT_DEPTH = J1_FINGER_DEPTH  # 11.43: full finger length, per Ven's board (fig 3-2 reads 0.36 in)
J1_KEY_SLOT_W = 0.91        # 3M: .036 +/- .004 (TEAC fig 103 agrees)
J1_KEY_BETWEEN = (4, 6)     # section 3.2: key slot between pins 4 and 6
J1_NARROW_PADS = {3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0} if J1_KEY_SLOT else {}   # 0.32 mm copper-to-slot when cut
J1_DROP_PADS = set()        # all 34 contacts present
# Handedness (established in the extender / activity-monitor projects):
# viewed from the COMPONENT side with the card edge pointing away, pin 2 is at the RIGHT.
# Even pins on the component side (F.Cu), odd pins on the solder side (B.Cu).

# ---------------------------------------------------------------- J2 power
# SA400L OEM manual section 3.3: AMP Mate-N-Lok 4 pins, pin 1 = +12 V, 2 = +12 RTN, 3 = +5 RTN,
# 4 = +5 V.  The SA400 carries it on the solder side; v0.2.0-0.2.3 copied that and JLCPCB's
# single-sided (Economic) PCBA left it unpopulated.  From v0.2.4 J2 is on the COMPONENT side,
# right-angle, mating face at the recessed rear edge (Ven, 2026-10-19).
#   Part: TE Commercial MATE-N-LOK right-angle 4-pos header 1-641737-1 (ENG_CD_641737); the
#   vertical 350211-1 (LCSC C305826, termination post 1.6 mm [.063], mating pin 2.1 mm) fits the
#   same pads and courtyard if the right-angle part is not in stock.
J2_PITCH = 5.08             # 0.200 in  TE centreline
J2_DRILL = 2.1              # TE post 1.6 mm -> 0.25 mm clearance; ASSUMED until the drawing is checked
J2_PAD = 3.6
J2_ROW_Y = 19.05            # pin row 7.62 mm behind the recessed rear edge - ASSUMED
J2_LAYER = "F.Cu"
# Pin-1 end.  Moving a header from the solder side to the component side MIRRORS it: the
# bottom-side layout (0.2.0-0.2.3) had pin 1 at x = 27.94 (nearest the board centre) viewed from
# the top; the same header on the top side puts pin 1 at the H1 end.  Both rest on the ASSUMED
# handedness of the TE header (pin 1 on the header's left when standing on its tails, mating face
# away from you).  BENCH CHECK before power (docs/TODO.md): header in the holes, drive plug on,
# continuity yellow wire -> the pad marked +12V.  If it lands on +5V instead, set J2_PIN1_X to the
# other end (27.94 with J2_PIN_DIR = -1) and rebuild.
J2_PIN1_X = 12.70           # pin 1 at the H1 end for a component-side header - ASSUMED (see above)
J2_PIN_DIR = +1             # +1: pins 2..4 run toward the board centre; -1: toward the corner

# ---------------------------------------------------------------- mounting
MOUNT_HOLE_DRILL = 3.2      # M3 / #4-40 clearance.  NOTE: the real SA400 PCB is held by
MOUNT_HOLE_PAD = 6.0        # four snap clamps (P/N 54036), not screws.  Holes are a
MOUNT_HOLES = [             # deliberate deviation for a standalone board.
    (6.35, 30.48), (133.35, 38.10), (6.35, 120.65), (133.35, 120.65),
]

# ---------------------------------------------------------------- fab rules (JLCPCB 2-layer)
TRACE_W = 0.4
POWER_W = 0.6
CLEARANCE = 0.3 
VIA_DRILL = 0.4
VIA_DIA = 0.8
EDGE_CLEARANCE = 0.5        # copper to board edge; JLC minimum 0.3
GRID = 1.27                 # routing grid

# ---------------------------------------------------------------- LEDs
LED_R = 470                 # ohms: ~5.5 mA with the standard-brightness LEDs JLCPCB stocks (v0.2.3); 1k5 for high-efficiency parts
LED12_R = 2200              # ohms: +12 V indicator series, ~4.5 mA
PULLUP_R = 10000
