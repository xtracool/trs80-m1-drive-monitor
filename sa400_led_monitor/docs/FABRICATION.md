# Fabrication — JLCPCB order guide, sa400_led_monitor v0.2.4

## Files

`output/gerbers/` contains everything JLCPCB needs (plotted by KiCad 10.0.6 kicad-cli, Gerber X2 + Excellon):

| File | Layer |
|---|---|
| `sa400_led_monitor-F_Cu.gtl` / `-B_Cu.gbl` | copper |
| `-F_Mask.gts` / `-B_Mask.gbs` | solder mask |
| `-F_Silkscreen.gto` / `-B_Silkscreen.gbo` | silkscreen |
| `-Edge_Cuts.gm1` | outline, tab, key slot |
| `-PTH.drl` / `-NPTH.drl` | plated / non-plated drills |
| `-PTH-drl_map.gbr` / `-NPTH-drl_map.gbr` | drill maps (reference) |
| `-job.gbrjob` | job file |

`gen/verify.py` zips the folder as `output/sa400_led_monitor_v0.2.4_gerbers_JLCPCB.zip`.

**Upload only these three files to JLCPCB** (an order placed with the whole project zip as the "gerber"
is cancelled by their review — that happened on 2026-10-05):

| JLCPCB upload box | File |
|---|---|
| Add gerber file (PCB order) | `output/sa400_led_monitor_v0.2.4_gerbers_JLCPCB.zip` |
| PCBA → BOM | `output/assembly/BOM_jlcpcb.csv` (every line carries the LCSC number JLCPCB matched for the first order) |
| PCBA → CPL | `output/assembly/CPL_jlcpcb.csv` (45 rows, all Top since 0.2.4; U1A/U2A/U3A socket rows at the IC positions) |

PCBA remark (≤ 500 characters):

> U1-U3: ICs fitted into DIP-14 sockets U1A-U3A (same positions), notch per silk. J2 on TOP side,
> right-angle, mating face toward the recessed edge, pin1=square pad at the H1 end. Q1 TO-220 pin order G-D-S, gate=square pad, metal
> tab toward the J2 edge. LEDs D1-D8,D12,D13: cathode=square pad. D11 band=square pad. C4 + lead=square
> pad. J1 gold fingers: no parts. 1.6mm holes at finger root and H1-H4 are non-plated, leave empty.
> Photo confirm top AND bottom.

## Order options

| Option | Choose | Why |
|---|---|---|
| Layers | 2 | |
| Dimensions | 139.7 × 127 mm (auto-detected) | |
| Thickness | **1.6 mm** | 3M connector spec 1.37–1.78 mm |
| Copper | 1 oz | |
| Surface finish | **ENIG** | required under the fingers; HASL is not acceptable on a card edge |
| Gold fingers | **Yes** | hard gold on the tab |
| Bevel / chamfer on fingers | **Yes** | JLCPCB bevels at 30°, 0.6 mm deep; the finger copper starts 0.66 mm from the edge to suit it |
| Solder mask | any | |
| Silkscreen | white | |
| Via covering | Tented | |
| Board outline tolerance | ±0.2 mm | |
| Confirm production file | Yes | |
| Castellated holes / edge plating / blind slots / humidity card | No | |
| Stencil | No | all through-hole |
| PCBA | **Economic (single-sided) is enough since 0.2.4** — every part is on the top; confirm placement, photo confirmation | the 0.2.3 order was Economic with J2 on the back, so J2 was skipped |

JLCPCB detects the gold-finger option from the fingers on the tab; if the reviewer asks, the fingers are the
17 pads on each side of the 45.59 mm tab at the rear edge and the bevel applies to that edge only.

## Design-rule margins used

| Rule | Board | JLC minimum |
|---|---|---|
| Trace width | 0.40 signal / 0.60 power | 0.127 |
| Clearance | 0.30 | 0.127 |
| Via | 0.80 / 0.40 drill | 0.45 / 0.20 |
| Copper to edge | 0.50 (0.32 at the key slot, 0.66 at the fingers) | 0.30 |
| Slot width | 0.91 | 0.65 routed |

## Verification already done (KiCad 10.0.6, `kicad-cli`, via `gen/verify.py`)

| Check | Result |
|---|---|
| `pcb drc --schematic-parity --severity-all` | **0 violations, 0 unconnected, 0 parity issues** (`output/drc.json`) |
| `sch erc --severity-all` | **0 violations** (`output/erc.json`) |
| Footprint ↔ symbol links | 47 / 47 |
| Update-PCB metadata (sheetname, sheetfile, unit pins) | matches KiCad's netlist export |
| Gerber / drill plot | `output/gerbers/`, 12 files, zipped for upload |
| BOM ↔ CPL | same 45 designators (42 parts + 3 socket rows) |
| GND zone | filled and saved in the board file |

## Before you upload

1. Open `kicad/sa400_led_monitor.kicad_pro` in KiCad 10.
2. Re-run the checks yourself: `python3 gen/verify.py --kicad-bin "C:/Program Files/KiCad/10.0/bin"` or `gen/check.ps1`.
3. Confirm the three measurements in `docs/TODO.md`; if any changes, rebuild and re-plot.
4. Upload the gerber zip, BOM and CPL listed above — nothing else.

## Answering a JLCPCB engineering query

JLCPCB may send a 3D render and ask whether polarized THT parts are oriented correctly (they did for the
0.2.2 order on 2026-10-07, because the 0.2.2 silkscreen drew the Q1 body box on the wrong side of the
pin row). The authoritative orientations are in `docs/ASSEMBLY.md` §"Polarity"; reply with that list and
an annotated copy of their render. The 0.2.3 silkscreen shows the TO-220 body, tab line and G/D/S labels, so
the render and the silk agree.
