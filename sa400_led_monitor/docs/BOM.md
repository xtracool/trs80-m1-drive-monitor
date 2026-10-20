# Bill of Materials — sa400_led_monitor v0.2.4

Document: `BOM.md` · 2026-10-19 · All parts through-hole. Quantities per board.
Machine-readable copies: `output/BOM.csv`, `output/assembly/BOM_jlcpcb.csv` (with the LCSC numbers below).
LCSC numbers are the parts JLCPCB matched and we accepted for the first assembled batch.

## Active

| Qty | Ref | Part | Package | Example part / source |
|---|---|---|---|---|
| 1 | U1 | 74LS14 hex Schmitt-trigger inverter | DIP-14 | TI SN74LS14N (LCSC C73064) — https://www.ti.com/product/SN74LS14 · https://www.mouser.com/c/?q=SN74LS14N |
| 1 | U2 | 74LS00 quad 2-input NAND | DIP-14 | TI SN74LS00N (LCSC C181629) — https://www.ti.com/product/SN74LS00 · https://www.mouser.com/c/?q=SN74LS00N |
| 1 | U3 | 74LS06 hex inverter, open-collector | DIP-14 | TI SN74LS06N (LCSC C22384767) — https://www.ti.com/product/SN74LS06 · https://www.mouser.com/c/?q=SN74LS06N |
| 3 | U1A–U3A | DIP-14 IC socket | DIP-14 | any dual-wipe 14-pin socket (LCSC C190815) |

## Protection and indicators

| Qty | Ref | Part | Package | Example part / source |
|---|---|---|---|---|
| 1 | F1 | PTC resettable fuse, 0.5 A hold / 1 A trip, ≥ 16 V | radial 5.08 mm | A72-050 (LCSC C135425) or Littelfuse RUEF050 — https://www.mouser.com/c/?q=RUEF050 |
| 1 | Q1 | P-channel MOSFET, pins **G-D-S** | TO-220 vertical, tab toward the J2 edge | IRF4905PBF (LCSC C2564) — https://www.mouser.com/c/?q=IRF4905PBF · logic-level alternative onsemi NDP6020P — https://www.mouser.com/c/?q=NDP6020P |
| 1 | D11 | Zener 5.6 V 5 W, +5 V rail clamp | DO-15 vertical | 1N5339B (LCSC C5444832) — https://www.mouser.com/c/?q=1N5339B |
| 2 | D12, D13 | Yellow 5 mm LED, standard brightness ("12V" / "5V" present) | 5 mm | Kingbright WP483YDT (LCSC C6001325) — https://www.mouser.com/c/?q=WP483YDT |

Zener band (cathode) and LED cathodes go in the **square** pads. Q1: gate is pin 1 (square pad), metal tab toward the J2 edge — the silk shows the body, tab line and G/D/S.

## Drive-state LEDs

| Qty | Ref | Part | Package | Example part / source |
|---|---|---|---|---|
| 4 | D1–D4 | Red 5 mm LED, standard brightness, Vf ≈ 1.9 V | 5 mm | Kingbright L-53ID (LCSC C598429) — https://www.mouser.com/c/?q=L-53ID · high-efficiency WP7113LID also fits (then R1–R4 = 1.5 kΩ) |
| 4 | D5–D8 | Green 5 mm LED, standard brightness, Vf ≈ 2.1 V | 5 mm | Kingbright WP7113GD (LCSC C7117617) — https://www.mouser.com/c/?q=WP7113GD · high-efficiency WP7113LGD also fits (then R5–R8 = 1.5 kΩ) |

Cathode = shorter lead / flat side of the rim, into the **square** pad (pin 1).

## Passives

| Qty | Ref | Value | Package | Notes |
|---|---|---|---|---|
| 8 | R1–R8 | 470 Ω ±5 % ¼ W | axial, vertical 7.62 mm | LED series, ≈ 5.5 mA (YAGEO MFR-25JT-52-470R, LCSC C176518). Use 1.5 kΩ with high-efficiency LEDs (≈ 1.8 mA). |
| 5 | R9–R13 | 10 kΩ ±5 % ¼ W | axial, vertical 7.62 mm | Bus input pull-ups (YAGEO MFR-25JT-52-10K, LCSC C176451) |
| 5 | R14–R18 | 470 Ω ±5 % ¼ W | axial, vertical 7.62 mm | Bus series / fault-limiting (between finger and receiver) (LCSC C176518) |
| 1 | R19 | 2.2 kΩ ¼ W | axial, vertical 7.62 mm | +12 V indicator series, ≈ 4.5 mA (YAGEO MFR-25FTE52-2K2 1 %, LCSC C172997) |
| 1 | R21 | 470 Ω ±5 % ¼ W | axial, vertical 7.62 mm | +5 V indicator series, ≈ 6 mA (LCSC C176518) |
| 4 | C1, C2, C3, C6 | 100 nF 50 V ceramic | disc, 2.5 mm pitch | IC decoupling (C1–C3), rail entry (C6) (LCSC C45664, 2.0 mm pitch fits the pads) |
| 1 | C4 | 10 µF 16 V electrolytic | radial 5 mm dia, 2.5 mm pitch | Bulk on +5 V. **+ lead in the square pad.** (LCSC C53330112) |

## Connectors and hardware

| Qty | Ref | Part | Source |
|---|---|---|---|
| — | J1 | 34-contact card edge, part of the PCB (gold fingers, bevel — fab option) | — |
| 1 | J2 | TE Commercial Mate-N-Lok 4-position **right-angle** PCB header **1-641737-1**, component side (SA400 pinout: 1 +12 V indicator, 2/3 RTN, 4 +5 V logic) | https://www.te.com/en/product-1-641737-1.html · https://www.mouser.com/c/?q=1-641737-1 · https://www.digikey.com/en/products/result?keywords=1-641737-1 — if unavailable, the **vertical** 350211-1 fits the same pads (LCSC C305826, https://www.te.com/en/product-350211-1.html) |
| 4 | H1–H4 | M3 × 6 mm standoff + M3 screw, or #4-40 | any |

## Mating parts (not on the board)

| Item | Part | Source |
|---|---|---|
| Bus cable connector | 3M 3463-0001, 34-way card-edge IDC | datasheet https://multimedia.3m.com/mws/media/22013O/3m-tm-100-in-card-edge-connector-w-o-mounting-flng-ts0010.pdf · https://www.mouser.com/c/?q=3463-0001 |
| Key plug for the pin 4/6 slot | 3M 3439-2 | https://www.mouser.com/c/?q=3439-2 |
| Power plug | AMP 1-480424-0 housing + 60619-1 pins (standard drive power connector) | https://www.te.com/en/product-1-480424-0.html |

## PCB

| Item | Spec |
|---|---|
| Size | 139.70 × 127.00 mm (5.5 × 5.0 in), 45.59 mm tab protruding from the recessed rear edge |
| Layers / copper | 2, 1 oz |
| Thickness | 1.6 mm (3M spec 1.37–1.78) |
| Finish | ENIG, **gold fingers + bevel** selected in the JLCPCB order options |
| Fab | JLCPCB, gerbers in `output/gerbers/` |

## Cost estimate (single board, 2026 distributor pricing)

| Group | Approx |
|---|---|
| ICs + sockets | $4 |
| Protection + indicators (PTC, MOSFET, Zener, 2 LEDs) | $3 |
| Drive LEDs | $2 |
| Passives | $1 |
| J2 | $1 |
| Standoffs | $1 |
| PCB (JLCPCB, 5 pcs, gold-finger option) | $25–35 for the batch |
