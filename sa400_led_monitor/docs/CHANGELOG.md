# Changelog

## v0.2.4 — 2026-10-19 — J2 on the component side
- **J2 moved to the component side**, right-angle, mating face at the recessed rear edge (TE Commercial
  Mate-N-Lok 1-641737-1; the vertical 350211-1 / LCSC C305826 fits the same pads and courtyard). Reason:
  JLCPCB's Economic PCBA is single-sided placement, and J2 was the only bottom-side part on the 0.2.3
  order, so it came back unpopulated. All 45 placements are now Top.
- Pin 1 at the H1 (corner) end, x = 12.70, pins toward the board centre — the mirror of the solder-side
  layout, same ASSUMED header handedness; `J2_PIN_DIR` added so the end can be flipped from config. The
  bench continuity check (yellow wire → `+12V` pad) is now a TODO item and an ASSEMBLY.md step.
- Power row (F1, Q1, D11, C6, C4, R19, D12, R21, D13) moved from y 30.48 to 33.02 so the J2 labels
  (`1 +12V … 4 +5V`, "J2 PWR IN – SA400 pinout", below the housing) clear the Q1/F1
  references; "12V"/"5V" silk moved with it. Component-side J2 pin-number/function labels of 0.2.2–0.2.3
  and the solder-side labels are gone (nothing on the back now but the GND pour and the version text).
- Footprint renamed `MateNLok_4_RA` (was `MateNLok_4_RA_350211-1`); J2 value `AMP 1-641737-1`; JLCPCB BOM
  leaves J2's LCSC blank (consign the right-angle part or match C305826 for the vertical one).
- Docs: THEORY §4.0 (why moving a header between sides mirrors pin 1), MECHANICAL, ASSEMBLY (handedness
  check), FABRICATION (Economic tier is enough), BOM, TODO. Copper re-routed by the generator (power row
  moved); DRC/ERC/links/F8 emulation re-verified.
- Merged from the bring-up session (same day, worked on the 0.2.2 tree):
  - Docs (2026-10-19): `docs/TEST_PLAN.md` added — three-phase bring-up plan (unpowered, bench supply with
    bus-simulator jig and protection tests, on the Model I EI), written against the r2 as-built BOM.
  - Docs (2026-10-19, test plan 1.1): §0.7 populated-board wireframe + legend; `gen/render_populated.py`
    draws it from `design.py`; `pdf/build_test_plan.py` builds the test-plan PDF (LuaLaTeX via pandoc).
  - Docs (2026-10-19, design review, test plan 1.2): receiver low-level margin found thinner than documented —
    THEORY §3.0 omitted the pull-up current through the 470 Ω (worst case ≈ 0.79 V at U1 vs V_T− 0.5 V min);
    §3.0/§4.2/§4.3 corrected in red. TEST_PLAN §0.8 lists the findings, adds 3.2.5/3.3.7 (U1 input node on
    the real bus), loosens 2.6.17 to < 0.45 V, and marks 2.7.2/2.7.4 as able to damage D12/D11. V0.3_PLAN
    gains the carry-over fixes: 74HCT14 receivers, pull-ups on the finger side (100 k), 1N4148 with D12.
    `pdf/color_spans.lua` renders the red/blue Markdown spans in the test-plan PDF.
  - Docs (2026-10-19, test plan 1.3): drawings moved out of the front matter into appendices — A board wireframe
    (+ legend on its back), B one-page schematic (`pdf/schematic.tex`, circuitikz, as-built values and DIP pin
    numbers), C as-built parts list; each appendix starts on a right-hand page for double-sided printing.
    Design-review section renumbered §0.8 → §0.7.
  - Docs (2026-10-19, test plan 1.4): Appendix D test-fixture drawings (`pdf/fixtures.tex`: bus-simulator jig,
    J2 power pigtail with meter, key-plug position) and Appendix E cable drawing (landscape page); every
    appendix on its own sheet with a blank back.

## v0.2.3 — 2026-10-07 — Q1 silkscreen, as-built values, JLCPCB BOM
- **Q1 footprint:** the TO-220 silkscreen box and courtyard were drawn on the +y side of the pin row; a
  vertical TO-220 with pin 1 at −x stands over the pins with its metal tab at −y (Vishay TO-220 drawing,
  KiCad `TO-220-3_Vertical`). JLCPCB's engineer queried the mismatch on their 3D render (2026-10-07);
  their render was electrically correct. Silk now shows the body outline, the tab line, "TAB", and
  G / D / S under the pads; F.Fab body added; courtyard y −3.4…+1.9. The component-side "J2 PWR IN"
  label moved from y 25.4 to 24.3 to clear the relocated Q1 reference. Copper, drills and outline unchanged.
- **As-built values:** R1–R8 and R21 1k5 → **470R**, R19 4k7 → **2k2** (standard-brightness LEDs from
  JLCPCB stock: L-53ID, WP7113GD, WP483YDT); Q1 value NDP6020P → **IRF4905PBF** (the G-D-S part JLCPCB
  stocks; NDP6020P stays the logic-level alternative). Schematic, BOM and theory of operation updated;
  +5 V budget ≈ 45 mA, +12 V indicator 4.5 mA.
- **JLCPCB BOM/CPL:** `build.py` now writes the LCSC numbers JLCPCB matched for the first order
  (`JLC` table) and lists the sockets as U1A/U2A/U3A; `verify.py` adds the three socket rows to the CPL
  at the IC positions, checks BOM ↔ CPL (45 designators) and zips the gerbers as
  `output/sa400_led_monitor_v0.2.3_gerbers_JLCPCB.zip`.
- Docs: FABRICATION (upload only the three files; order options; remark; how to answer an engineering
  query), ASSEMBLY (polarity table), BOM (LCSC column), MECHANICAL (Q1 geometry), TODO.
- History: the first PCBA order (2026-09-28) was cancelled because the whole project zip had been uploaded
  as the gerber file; re-ordered 2026-10-05 with the gerber zip + hand-edited r2 BOM/CPL, which this
  release reproduces from the generator.

## v0.2.2 — 2026-09-08 — J2 labelling
- Docs (later the same day): `docs/V0.3_PLAN.md` records the decided next board (LED-bar modules,
  74HCT244 per drive, TTL); TODO.md v0.3 section updated; JLCPCB upload zip added to `output/`.
- Fix: `output/assembly/BOM_jlcpcb.csv` and `CPL_jlcpcb.csv` had been left over from v0.1 (34 parts,
  old positions). BOM is now written by `build.py`, CPL by `verify.py` from KiCad's position export,
  and the gate checks the two list the same designators (42 placements + 3 sockets).
- J2 now labelled on both sides: component side has pin numbers 1–4 above the pads and +12V / RTN / RTN /
  +5V below them; solder side (footprint silk, outside the housing) has "1 +12V 2 RTN 3 RTN 4 +5V" and
  "PWR IN - SA400 pinout - pin 1 square".
- Fix: the solder-side housing outline was mirrored (drawn behind the pins instead of toward the rear
  edge). Back-side geometry is now pre-mirrored so KiCad's flip lands it where designed; the library copy
  follows the same convention (library parity still clean).

## v0.2.1 — 2026-09-08 — SA400 power usage restored, protection kept
- Logic powered from the PSU **+5 V** pin as on the SA400; +12 V pin lights a "12 V present" indicator.
  Chain: J2-4 → F1 PTC 0.5 A → Q1 NDP6020P P-MOSFET reverse-polarity switch (0.002 V drop) → +5 V with
  D11 1N5339B 5.6 V clamp, C6, C4. D13 "5 V" and D12 "12 V" indicators.
- Removed the 7805, 1N5819, P6KE18A, C5, C7 of v0.2.0. Series 470 Ω bus resistors retained.
- Fault table updated (THEORY §4.3). 47 footprints; DRC 0/0/0, ERC 0, links 47/47, F8 emulation clean.
- Six markdown docs (README, BOM, MECHANICAL, FABRICATION, ASSEMBLY, TODO) had been shipped empty since
  v0.1.3 by a versioning bug; all rebuilt, and `gen/verify.py` now fails on an empty doc.

## v0.2.0 — 2026-09-08 — regulated power and bus protection
- Board now powered from **+12 V** (J2 pin 1) through F1 PTC 0.5 A → D9 1N5819 (reverse) → VIN
  (D10 P6KE18A TVS, C5 10 µF/25 V, C6 100 nF) → U4 7805 → +5 V (C7 100 nF, D11 1N5339B 5.6 V clamp,
  C4 10 µF). PSU +5 V pin unused; both returns to GND.
- 470 Ω series resistors R14–R18 between each monitored finger and its pull-up/receiver node
  (nets `DSn_n` = finger, `DSn_in` = receiver side). Worst-case current into an EI driver ≤ 11 mA.
- Fault analysis in THEORY_OF_OPERATION §4; BOM, schematic, placement, routing regenerated.
- 47 footprints; KiCad 10 DRC 0/0/0, ERC 0, links 47/47, F8 emulation clean.

## v0.1.4 — 2026-09-08
- F8 (*Update PCB from Schematic*) on v0.1.3 matched every part but still listed three metadata
  updates per footprint: sheetname, sheetfile and "unit metadata" (KiCad 10's per-unit pin list used
  for gate swapping). `gen/postprocess.py` now writes all three, taking the unit/pin lists from
  KiCad's own netlist export so they compare equal in the updater.
- `gen/verify.py` step 5b emulates the updater's dry-run comparisons (footprint id, value,
  sheetname, sheetfile, unit pin lists) from the exported netlist; a negative test confirms it flags
  a board that lacks the metadata.
- Board file otherwise unchanged; all outputs regenerated.

## v0.1.3 — 2026-09-07
- **Fix:** footprint links used `/<root-sheet-uuid>/<symbol-uuid>`; KiCad's root-sheet form is
  `/<symbol-uuid>` (checked against KiCad 10's own `demos/ecc83`). v0.1.2 therefore still offered to add
  every part in *Update PCB from Schematic*. Corrected; `gen/verify.py` now checks this form.
- `gen/verify.py` added: build → KiCad postprocess → DRC+parity → ERC → link check → gerber/drill plot,
  nonzero exit on any failure. Nothing is packaged unless it passes.
- Not headlessly testable: the F8 dialog itself — run it once after opening the project.
- Docs (2026-09-08): per-side copper views (`output/copper_top.png`, `copper_bottom.png`) and isolated
  GND / +5V net images (`output/net_gnd.png`, `net_5v.png`, from `gen/render_nets.py`) added to the
  design PDF; the raytraced renders hide copper under the mask and had prompted a false "no ground" read.

## v0.1.2 — 2026-09-07
- Footprints now carry `(path "/<root>/<symbol-uuid>")` links to deterministic schematic symbol UUIDs
  (`uuid5(ref)`), so **Update PCB from Schematic** reports no changes instead of trying to add every
  part again. Verified: 34/34 linked, KiCad 10 DRC parity 0, ERC 0.
- `docs/ASSEMBLY.md` + `output/assembly/` (JLCPCB BOM/CPL, KiCad position file).
- All fab outputs, renders and the design PDF regenerated as v0.1.2.

## v0.1.1 — 2026-09-07
Verification pass with KiCad 10.0.6 (kicad-cli DRC/ERC, pcbnew API).
- Finger copper set back 0.66 mm from the insertion edge (3M .026; JLCPCB bevel rule ≥ 0.6 mm).
- Pull-ups spaced to 5.08 mm, LED pairs to 7.62 mm (courtyards were overlapping).
- No-connect pads carry KiCad's `unconnected-(…)` nets → schematic parity exact.
- All footprints moved into the project library `sa400.pretty`; symbols into `sa400.kicad_sym`
  with project lib tables.
- J2 written front-side and flipped by KiCad itself (`gen/postprocess.py`), which also fills the
  GND zone and saves the board in native KiCad 10 format.
- J2 pins 3/4 typed power_out so ERC sees the supply; symbol placement snapped to 1.27 mm.
- Silkscreen: 0.8 mm text, cap outlines off the pads, labels de-overlapped.
- Result: DRC 0 / unconnected 0 / parity 0, ERC 0. Gerbers, drills, STEP re-exported from 10.0.6.

## v0.1.0 — 2026-09-05
First complete design.
- Board 5.5 × 5.0 in, rear edge recessed 11.43 mm, J1 tab per 3M TS-0010-14 (45.59 mm,
  1.40 mm contacts, 10.16 mm long, R1.02 corners), key slot 0.91 × 11.43 between pins 4/6,
  two Ø1.6 NPTH clip holes on the root line under pins 2 and 34, pin 2 5.08 mm from the corner.
- J2 AMP 350211-1 on the solder side, +5 V only.
- 74LS14 receivers + 10k pull-ups, 74LS06 → red (DSn), 74LS00 → green (DSn·WG), 1k5 LEDs.
- Generated KiCad 7-format project (opens in 9), validated by kicad-cli 7.0.11: gerbers and
  drills plotted, schematic netlist matches PCB 111/111 pins.
- Python maze router, 0.30 mm clearance, independent geometric DRC clean.
- Docs: THEORY_OF_OPERATION, BOM, CABLE (6-connector Model I cable), MECHANICAL, FABRICATION.

### J1 revision history within v0.1.0 (from Ven's photo and the 3M drawing)
1. notches → full-length rear recess; 2. all 34 fingers restored; 3. key slot cut, full
finger depth; 4. tab width 45.59 per 3M; 5. clip holes moved onto the root line, non-plated.
