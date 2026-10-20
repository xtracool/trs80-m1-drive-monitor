# JLCPCB upload — sa400_led_monitor v0.2.2 (r2 fab set)

Document: `JLCPCB_UPLOAD_v0.2.2.md` · 2026-10-05 · board rev v0.2.2 · fab-file set r2

**Upload only the three files below. Do not upload the project zip (`sa400_led_monitor_v0.2.2.zip`) — it
contains source, docs and renders, and JLCPCB cancels orders whose "gerber" upload is not a gerber set.**

| JLCPCB upload box | File | Contents |
|---|---|---|
| **Add gerber file** (PCB order page) | `sa400_led_monitor_v0.2.2_gerbers_JLCPCB.zip` (130 kB, md5 `e14e28a9…`) | 12 files: F/B copper, F/B mask, F/B silkscreen, Edge_Cuts, PTH + NPTH Excellon drills, 2 drill maps, `.gbrjob`. KiCad 10.0.6, project revision tag `v0.2.2`. |
| **PCBA → BOM file** | `BOM_jlcpcb_v0.2.2_r2.csv` | 17 lines, every line has an LCSC part number (see table below). |
| **PCBA → CPL / pick-and-place file** | `CPL_jlcpcb_v0.2.2_r2.csv` | 45 placements: 44 Top, J2 Bottom. Includes U1A/U2A/U3A socket rows at the IC positions. |

Nothing else is needed. `remark.txt` is the text to paste into the PCBA "Remark" box (399 chars, limit 500).

## PCB options

| Option | Value |
|---|---|
| Base material | FR-4 |
| Layers | 2 |
| Dimensions | 139.7 × 127 mm (auto-read from Edge_Cuts; accept) |
| Quantity | 5 |
| Thickness | 1.6 mm |
| Surface finish | **ENIG** |
| Outer copper | 1 oz |
| Gold fingers | **Yes** |
| 30° finger chamfer | **Yes** |
| Gold thickness | default (thinnest offered) |
| Via covering | Tented |
| Board outline tolerance | ±0.2 mm |
| Confirm production file | Yes |
| Castellated holes / edge plating / blind slots / humidity card | No |
| Stencil | No (all through-hole) |
| Remove order number | optional |

## PCBA options

| Option | Value |
|---|---|
| Assembly side | **Both** (J2 is on the bottom) |
| Qty assembled | 5 |
| Confirm parts placement | Yes |
| Photo confirmation | Yes — top **and** bottom |
| Remark | paste `remark.txt` |

## Parts in the BOM (all matched to JLCPCB stock)

| Ref | Part | LCSC | Origin of the choice |
|---|---|---|---|
| C1 C2 C3 C6 | 100 nF ceramic disc | C45664 | JLCPCB evaluation (2.0 mm pitch on 2.54 mm pads — accepted) |
| C4 | 10 µF 16 V radial | C53330112 | JLCPCB evaluation |
| D1–D4 | Kingbright L-53ID red 5 mm | C598429 | JLCPCB evaluation |
| D5–D8 | Kingbright WP7113GD green 5 mm | C7117617 | JLCPCB evaluation |
| D11 | 1N5339B 5.6 V 5 W Zener | C5444832 | JLCPCB evaluation |
| D12 D13 | Kingbright WP483YDT yellow 5 mm | C6001325 | JLCPCB evaluation |
| F1 | A72-050 PTC 0.5 A | C135425 | JLCPCB evaluation |
| J2 | TE 350211-1 Mate-N-Lok | C305826 | JLCPCB evaluation |
| Q1 | IRF4905PBF (G-D-S, TO-220) | C2564 | JLCPCB follow-up (NDP6020P out of stock) |
| R9–R13 | 10 k YAGEO MFR-25JT-52-10K | C176451 | same MFR-25 series as the 470 R JLCPCB chose |
| R1–R8, R14–R18, R21 | 470 R YAGEO MFR-25JT-52-470R | C176518 | JLCPCB evaluation; R1–R8/R21 changed 1k5 → 470 R because the chosen LEDs are standard brightness (≈ 6 mA) |
| R19 | 2k2 YAGEO MFR-25FTE52-2K2 (1 %) | C172997 | changed 4k7 → 2k2 for the same reason (≈ 4.5 mA on +12 V) |
| U1 | SN74LS14N | C73064 | JLCPCB catalogue |
| U2 | SN74LS00N | C181629 | JLCPCB catalogue |
| U3 | SN74LS06N(LX) | C22384767 | JLCPCB follow-up |
| U1A U2A U3A | DIP-14 socket | C190815 | JLCPCB follow-up; ICs are fitted into the sockets |

If a part shows "no stock" at upload time, pick any same-value alternative in the JLCPCB parts dialog —
every value here is generic except Q1 (must be a **G-D-S** P-channel logic-level MOSFET in TO-220).

## First power-up (unchanged from FABRICATION.md)

No ribbon cable attached: apply the drive power plug, D12 (12V) and D13 (5V) should light, measure 5.0 V
between any IC pin 14 and pin 7. Only then connect the ribbon.

## TODO

- [ ] Fold these LCSC numbers and the 470 R / 2k2 values into `gen/build.py::write_jlc_bom()` and `docs/BOM.md`
      so the generator emits this BOM directly (v0.2.3). The r2 CSVs were edited by hand from the v0.2.2 outputs.
- [ ] When boards arrive: confirm the three ASSUMED dimensions (`J1_TAB_CORNER_GAP`, `J1_KEY_SLOT_W`, `J2_DRILL`).
