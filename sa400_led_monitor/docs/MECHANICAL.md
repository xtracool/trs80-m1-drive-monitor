# Mechanical — sa400_led_monitor v0.2.4

Every dimension below is in `gen/config.py`; change it there and rebuild. Origin is the top-left corner
of the outline in KiCad; +y runs toward the front (LED) edge.

## Board

| Item | Value | Source |
|---|---|---|
| Outline | 139.70 × 127.00 mm (5.5 × 5.0 in) | Ven |
| Thickness | 1.6 mm | 3M TS-0010 (1.37–1.78); SA400L fig 3-2 (0.062 in) |
| Rear edge | recessed 11.43 mm along its full length; only the J1 tab reaches y = 0 | Ven's SA400 PCB photo |

## J1 card-edge tab (3M TS-0010-14 sheet 3, "Recommended PCB Layout", 34-way)

| Item | Value | Source |
|---|---|---|
| Tab width (dim A) | 45.59 mm (1.795 ± .005 in), x = 89.03–134.62 | 3M |
| Tab depth | 11.43 mm (.450 min) | 3M / SA400L |
| Tab corner radius | 1.02 mm (R.040) | 3M |
| Contact pitch | 2.54 mm × 16, non-cumulative | 3M |
| Contact width | 1.40 mm (.055 ± .005) | 3M |
| Contact reach | 10.16 mm (.400 ± .015) from the insertion edge | 3M |
| Contact copper setback from the edge | **0.66 mm** (3M .026); JLCPCB requires ≥ 0.6 mm for the 30° bevel | 3M / https://jlcpcb.com/help/article/jlcpcb-gold-fingers |
| Pin 2 centre | x = 132.14 (2.475 from the tab edge) | fingers centred on A |
| Pin 34 centre | x = 91.50 | derived |
| Handedness | pin 2 at the right viewed from the component side, fingers away; odd pins on the solder side | SA400L §3.2 + photo |
| Pin-2 side, tab edge to board corner | 5.08 mm | **ASSUMED ±1.5**, scaled from the photo |
| Key slot | 0.91 mm wide (3M .036 ± .004) × 11.43 deep, between pins 4 and 6, x = 128.33 | width 3M / TEAC fig 103; depth Ven |
| Pads 3, 4, 5, 6 | narrowed to 1.0 mm → 0.32 mm copper-to-slot | derived |
| Clip holes | 2 × Ø1.6 mm **non-plated** at (132.14, 11.43) and (91.50, 11.43) — on the tab-root line, in line with pins 2 and 34, for the connector's retention clips | photo; Ø from SA400L fig 3-2 ".063 NOM (2X)" |
| Edge bevel | 30°, 0.6 mm (JLCPCB); 3M draws 45° × 1.02 | fab option |

## J2 power header (TE Commercial Mate-N-Lok, right-angle 1-641737-1, component side — since 0.2.4)

| Item | Value | Source |
|---|---|---|
| Pin pitch | 5.08 mm | TE |
| Pin row | y = 19.05 (7.62 behind the recessed edge) | **ASSUMED** |
| Pin 1 | x = 12.70 (H1 / corner end); pins run toward the board centre, pin 4 at x = 27.94 | **ASSUMED** — mirror of the 0.2.x solder-side layout (pin 1 at 27.94); header handedness unverified, see the bench check in THEORY §4.0 / TODO |
| Drill / pad | 2.1 / 3.6 mm | TE lists the 350211-1 termination post at 1.6 mm [.063]; 0.25 mm clearance. **ASSUMED** until ENG_CD_641737 is checked |
| Pinout | 1 +12 V (indicator), 2 +12 RTN, 3 +5 RTN, 4 +5 V (logic supply) — SA400 pinout; pin 1 = square pad | SA400L §3.3 |
| Housing | right-angle, on the component side; mating face at the recessed rear edge (y = 11.93), body to 4 mm behind the pin row (y = 23.05), x 8.70–31.94; outline on F.SilkS and F.Fab; the vertical 350211-1 sits inside the same outline | TE 1-641737-1 / 350211-1 |
| Labels | component side, below the housing: `1 +12V 2 RTN 3 RTN 4 +5V` under the pads (y = 25.05) and "J2 PWR IN – SA400 pinout" (y = 26.95) | since 0.2.4 |

## Power block

Row at y = 33.02 behind J2 (30.48 up to 0.2.3; moved one 2.54 step for the J2 labels), left to right:
F1 (13.97/19.05), Q1 TO-220 G-D-S (25.40/27.94/30.48; body straddles the pins from y = 29.87 (metal tab,
toward J2) to y = 34.27 (label face), per the Vishay TO-220 drawing / KiCad `TO-220-3_Vertical` — 0.2.2
drew the box on the +y side, fixed in 0.2.3), D11 (36.83, vertical 10.16), C6 (41.91), C4 (48.26), R19 (54.61), D12 (59.69), R21 (66.04),
D13 (71.12). Bus pull-ups R9–R13 at x = 77.47…87.63, y 19.05–26.67. Series resistors R14–R18 at
x = 104.14 / 111.76 / 116.84 / 121.92 / 127.00, y 17.78–25.40, under the fingers.

## Mounting

| Item | Value | Note |
|---|---|---|
| H1–H4 | Ø3.2 mm NPTH at (6.35, 30.48), (133.35, 38.10), (6.35, 120.65), (133.35, 120.65) | The real SA400 PCB is held by four snap clamps (P/N 54036); screw holes are a deliberate deviation for a standalone board. H2 is lowered to clear the cable connector body. |

## To measure before ordering (all one-line config changes)

1. `J1_TAB_CORNER_GAP` — tab edge to board corner on your SA400 (currently 5.08).
2. `J1_KEY_SLOT_W` — thickness of the 3M 3439-2 key plug on your cable (currently 0.91).
3. `J2_DRILL` — post diameter of the header you buy (currently 2.1 for the 1.6 mm TE post).
4. `J2_PIN1_X` / `J2_PIN_DIR` — header handedness, by the bench continuity check (yellow wire → +12V pad).
