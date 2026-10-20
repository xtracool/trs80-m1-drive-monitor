# TODO — sa400_led_monitor

## v0.2.x boards (5 populated ordered from JLCPCB, re-ordered 2026-10-05 with the fab files only)
- [ ] Measure tab-edge-to-corner on the SA400 PCB → `J1_TAB_CORNER_GAP` (5.08 assumed)
- [ ] Measure key plug thickness (3M 3439-2) → `J1_KEY_SLOT_W` (0.91)
- [ ] Confirm the header post diameter → `J2_DRILL` (2.1; TE lists the 350211-1 post at 1.6 mm) — https://www.te.com/en/product-1-641737-1.html
- [ ] **Bench-check J2 handedness** (header in holes, plug on, yellow wire → `+12V` pad) on the 0.2.3 boards; sets `J2_PIN1_X`/`J2_PIN_DIR` for 0.2.4 — see docs/ASSEMBLY.md
- [ ] 0.2.4: J2 moved to the component side (right-angle 1-641737-1 or vertical 350211-1); single-sided PCBA now covers every part
- [x] KiCad 10 DRC + ERC clean; schematic/PCB linked; F8 metadata emulated
- [ ] Run *Update PCB from Schematic* (F8) once in the GUI — expect an empty change list
- [x] LED resistor decided: 470R (standard-brightness LEDs from JLCPCB stock); R19 2k2 — schematic/BOM/docs at 0.2.3
- [x] JLCPCB BOM carries LCSC numbers; sockets listed as U1A–U3A with CPL rows (0.2.3)
- [x] Q1 silkscreen redrawn to the TO-220 convention (tab toward J2) after JLCPCB's 2026-10-07 query (0.2.3)
- [x] Reply to JLCPCB (orientation confirmed, 2026-10-07); boards received 2026-10-19
- [x] Power protection: PTC, P-MOSFET reverse switch, 5.6 V clamp, series bus resistors (0.2.2)

## Board bring-up — see docs/TEST_PLAN.md
- [ ] **J2 handedness check before any power** (TEST_PLAN to add): header in holes, drive plug on, continuity yellow wire → `+12V` pad; fit the header on whichever side passes
- [ ] Build the bus-simulator jig (TEST_PLAN §0.6)
- [ ] Board 1: Phase 1 → 2 (incl. protection tests 2.7/2.8) → 3
- [ ] Boards 2–5: Phase 1 → 2 (2.1–2.6) → 3 (3.3.1–3.3.4)
- [ ] TEST_PLAN 3.3.7 (design review F1): U1 input node on the terminated bus — ≤ 0.5 V clean; 0.5–0.8 V → fit a 74HCT14 in U1 (socket swap) and re-measure
- [x] Update docs/BOM.md and THEORY_OF_OPERATION.md to the r2 as-built values (done in 0.2.3; design-review corrections merged 2026-10-19)

## v0.3 — decided, see docs/V0.3_PLAN.md (starts after the v0.2.x test run)
- [ ] Four 8-bit common-cathode LED bar modules (one per drive) replace D1–D8
- [ ] 4 × 74HCT244 gated by the drive-select nodes; second 74LS14; 74LS123 for STEP/INDEX
- [ ] Six new bus lines: MOTOR ON, STEP, DIRECTION, TRACK 00, WRITE PROTECT, INDEX (each through 470 Ω)
- [ ] Confirm module colour split and resistor value (Ven)
- [ ] Design-review carry-overs (V0.3_PLAN): 74HCT14 receivers; pull-ups to the finger side of R14–R18, 100 kΩ; 1N4148 in series with D12; D11 value per 2.4.2
- [ ] Optional plated variant of the clip holes (deferred)

## Tooling
- [ ] Router: courtyard-aware silkscreen placement
- [ ] Router: DSN export so freerouting can be used for denser boards
- [ ] Rebuild `pdf/` (LuaLaTeX) whenever docs change — `python pdf/build_pdf.py`
