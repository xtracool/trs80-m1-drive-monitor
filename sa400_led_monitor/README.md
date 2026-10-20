# sa400_led_monitor v0.2.4

SA400 form-factor board that plugs onto the Shugart 34-pin floppy bus as a fifth "drive" and shows
drive-select (red) and write-gate (green) activity for four drives on eight LEDs. Same card-edge tab and
AMP Mate-N-Lok power header as a Shugart SA400, same power usage (+5 V logic, +12 V present); 5.5 × 5.0 in.
Protected: PTC fuse, P-MOSFET reverse-polarity switch, 5.6 V rail clamp, 470 Ω series resistors between the
bus and the receivers so a board fault cannot damage the host.

## Contents

| Path | What |
|---|---|
| `kicad/` | KiCad 10 project: `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `sa400.pretty/`, `sa400.kicad_sym`, lib tables — open the `.kicad_pro` |
| `output/gerbers/`, `output/sa400_led_monitor_v0.2.4_gerbers_JLCPCB.zip` | JLCPCB-ready Gerber X2 + Excellon, plotted by KiCad 10.0.6; the zip is what you upload |
| `output/drc.json`, `output/erc.json` | KiCad 10 DRC (with schematic parity) and ERC reports — both zero |
| `output/sa400_led_monitor_schematic.pdf` | schematic print |
| `output/sa400_led_monitor.step` | 3D STEP |
| `output/render_top.png`, `render_bottom.png` | KiCad 10 raytraced front and back (under solder mask) |
| `output/copper_top.png`, `copper_bottom.png` | F.Cu and B.Cu copper views — use these to check connectivity |
| `output/net_gnd.png`, `net_5v.png`, `net_5v_in.png` | GND, +5V and +5V input nets isolated |
| `output/placement.png`, `j1_vs_photo.png`, `j1_root_holes.png`, `j2_labels.png` | placement and labelling review images |
| `output/BOM.csv`, `output/assembly/` | BOM; JLCPCB BOM (with LCSC numbers) + CPL (incl. socket rows); KiCad position file |
| `pdf/sa400_led_monitor_design_v0.2.4.pdf` | complete design document, built by `pdf/build_pdf.py` from `pdf/template.tex` |
| `docs/THEORY_OF_OPERATION.md` | how the bus and the board work, from first principles; power and fault analysis |
| `docs/MECHANICAL.md` | every dimension with its source; the three left to measure |
| `docs/BOM.md` | bill of materials with sources |
| `docs/FABRICATION.md` | JLCPCB order options and pre-upload checklist |
| `docs/ASSEMBLY.md` | KiCad 10 pre-flight steps, assembler comparison |
| `docs/CABLE.md`, `output/cable.png` | six-connector TRS-80 Model I drive cable |
| `docs/TEST_PLAN.md` | bring-up test plan: unpowered → bench supply + bus-simulator jig → on the EI, with record sheets; §0.7 = 2026-10-19 design-review findings; appendices A board wireframe + legend, B schematic, C as-built parts list |
| `pdf/schematic.tex`, `docs/img/schematic.pdf` | one-page circuitikz schematic, as built, drawn from the `design.py` netlist (the KiCad print is `output/sa400_led_monitor_schematic.pdf`) |
| `docs/V0.3_PLAN.md` | next board: LED-bar modules + 74HCT244 per drive, decided, not started |
| `docs/TODO.md`, `docs/CHANGELOG.md` | |
| `gen/` | Python generator — the design source of truth |

## Regenerating

    python3 gen/build.py                                   # placement -> routing -> DRC -> kicad/, BOM, assembly files
    <kicad>/bin/python3 gen/postprocess.py kicad/sa400_led_monitor.kicad_pcb   # KiCad flips any back-side part (none since 0.2.4), fills zones, writes F8 metadata
    python3 gen/verify.py --kicad-bin "C:/Program Files/KiCad/10.0/bin"        # release gate: all of the above + DRC/ERC/links/plots
    gen/check.ps1                                          # Windows: same steps via PowerShell
    python3 gen/outputs.py --kicad-bin "C:/Program Files/KiCad/10.0/bin"        # review outputs: raytraced renders, copper views, schematic PDF, STEP, placement/net images
    python3 gen/render_populated.py          # output/board_populated.png/.pdf (wireframe, as-built values)
    python3 pdf/build_test_plan.py           # pdf/sa400_led_monitor_test_plan_v1.3.pdf from docs/TEST_PLAN.md (needs pandoc; builds pdf/schematic.tex too)
    python3 pdf/build_pdf.py                 # design PDF (LuaLaTeX) from pdf/template.tex + config VERSION + CHANGELOG.md + TODO.md

Exit codes: 0 ok, 1 build/DRC failure, 130 Ctrl-C.

All dimensions live in `gen/config.py` with their source in the comment; anything marked ASSUMED is listed
in `docs/MECHANICAL.md` with the config name to change.

## Status

v0.2.x: 5 populated boards on order at JLCPCB (re-ordered 2026-10-05 with the fab files only; engineering
query about Q1 orientation answered 2026-10-07 — their render was right, our 0.2.2 silkscreen was not).
0.2.3 = the 0.2.2 copper with the corrected Q1 silkscreen, the as-built values (470 Ω LED resistors, 2k2,
IRF4905PBF) and the LCSC-matched JLCPCB BOM. **0.2.4 (2026-10-19, not yet fabricated)** moves J2 to the
component side as a right-angle header so a single-sided PCBA order populates every part; the J2
handedness bench check in `docs/ASSEMBLY.md` must be done on the 0.2.3 boards before 0.2.4 is ordered.
KiCad 10 DRC (with schematic parity) and ERC both zero.
Three physical measurements remain to confirm on the first boards (`docs/TODO.md`).
