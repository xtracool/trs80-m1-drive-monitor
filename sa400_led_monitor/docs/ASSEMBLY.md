# Pre-flight in KiCad 10 and assembly options — sa400_led_monitor v0.2.4

## A. What to do in KiCad 10 before ordering (15 minutes)

1. **Open** `kicad/sa400_led_monitor.kicad_pro`. The `sa400` symbol and footprint libraries are
   project-local (`sym-lib-table`, `fp-lib-table`), so nothing should report as missing.
2. **Schematic → Inspect → Electrical Rules Checker.** Expect 0. (Four "ignored tests" are KiCad defaults.)
3. **Schematic → Tools → Update PCB from Schematic** (F8). Expect an empty change list — this proves the
   two files agree. History: v0.1.1 offered to *Add* every part (missing links), v0.1.3 listed
   sheetname/sheetfile/unit-metadata updates; both are generated now. If a build ever offers *Add* lines
   again, tick *Re-link footprints to schematic symbols based on their reference designators* instead of
   applying the adds.
4. **PCB → Edit → Fill All Zones** (B). The file ships filled; refilling is harmless.
5. **PCB → Inspect → Design Rules Checker**, with *Test for parity between PCB and schematic* ticked and
   *Report all errors for tracks* on. Expect 0 / 0 / 0.
6. **View → 3D Viewer**: everything on the front (J2 included since 0.2.4); key slot between pins 4
   and 6; the two clip holes under pins 2 and 34.
7. **Apply the three measurements** in `docs/TODO.md` if they differ — edit `gen/config.py`, run
   `python3 gen/build.py`, then `gen/verify.py` (or `gen/check.ps1`). Do **not** hand-edit the `.kicad_pcb`.
8. **Plot from KiCad** only if you changed something; otherwise the shipped `output/gerbers/` are current.
9. **Zip `output/gerbers/`** and upload: 1.6 mm, ENIG, gold fingers, bevel (see `docs/FABRICATION.md`).

## B. Who can populate it

The board is 100 % through-hole (3 DIPs, a TO-220, 10 LEDs, 15 resistors, 5 caps, PTC, Zener, and one
right-angle header on the **back**). That rules out SMT-only services and makes hand assembly the norm.

| Service | Through-hole? | Parts sourcing | Notes for this board |
|---|---|---|---|
| **JLCPCB PCBA** https://jlcpcb.com/pcb-assembly | Yes — hand/wave soldered THT, $3.50 setup + $0.0173 per joint | Their own library (LCSC) or **consigned** parts | Cheapest. All parts are in their library (BOM carries the LCSC numbers; Q1 is the IRF4905PBF they stock). All parts are on one side since 0.2.4, so the Economic (single-sided) tier covers the whole board — the 0.2.3 order lost J2 exactly because it was the lone bottom-side part. The right-angle 1-641737-1 may need consignment; the vertical 350211-1 (C305826) is in their library and fits the same pads. Sockets: list socket + IC in BOM/CPL and remark "fit IC into socket". |
| **PCBWay assembly** https://www.pcbway.com/pcb-assembly.html | Yes, turnkey | Buys from Mouser/DigiKey for you, or consigned | Most flexible for exact parts. Quote-based, slower and dearer for a handful. |
| **Screaming Circuits** https://www.screamingcircuits.com | Yes | Turnkey or consigned, US-based | Sensible for 5–10 boards. |
| **You, one evening** | — | `docs/BOM.md` | ≈ 110 solder joints plus 3 sockets. The right answer for 1–5 boards. |

### Files for JLCPCB / PCBWay in `output/assembly/` (BOM by `gen/build.py`, CPL by `gen/verify.py`; the gate checks they list the same designators)

| File | Format | Purpose |
|---|---|---|
| `BOM_jlcpcb.csv` | Comment, Designator, Footprint, LCSC Part #, notes | LCSC numbers are the parts JLCPCB matched for the first order (table in `gen/build.py::JLC`); sockets are listed as U1A/U2A/U3A. |
| `CPL_jlcpcb.csv` | Designator, Mid X, Mid Y, Layer, Rotation | Written by `gen/verify.py` from `kicad-cli pcb export pos` (KiCad centroids, Y negative as KiCad exports it — JLCPCB accepts KiCad pos files directly); all rows Top since 0.2.4; U1A/U2A/U3A socket rows duplicated from U1/U2/U3. |
| `kicad_pos.csv` | KiCad native | For any other assembler. |

### Fitting J2 by hand
The header goes on the **component side**, inside the silkscreen outline, mating face toward the
recessed rear edge; pin 1 (+12 V) into the square pad at the H1 end. Labels sit just below the housing.

**Before soldering — handedness check (every revision, every new header part):** push the header into
its holes, plug the drive power plug on, and check continuity from the plug's yellow (+12 V) wire to the
pad printed `+12V`. If it lands on `+5V`, do not solder: the header's pin 1 is at the other end from what
the footprint assumes — fit it on the other side of the board for this batch and flip `J2_PIN1_X` /
`J2_PIN_DIR` in `gen/config.py` for the next. The 0.2.3 boards (J2 pads on the solder side, pin 1 at the
board-centre end) get the same check; because JLCPCB left J2 off, the header can be fitted on whichever
side the check says.

### Polarity — the authoritative list (component side, J1 fingers at the top, LEDs at the bottom)

| Part | Square pad | Orientation |
|---|---|---|
| Q1 IRF4905PBF, TO-220 | pin 1 = **gate**, left | Body stands over the three pins; **metal tab toward the J2 edge** (top), plastic label face toward the board centre; silk shows the body outline, the tab line and G / D / S under the pads |
| D11 1N5339B | cathode band, upper pad | Vertical or horizontal mounting, band at the square pad |
| C4 10 µF | **+** lead, upper pad ("+" on silk) | Negative stripe toward the lower pad |
| D1–D8, D12, D13 5 mm LEDs | cathode = flat side = short lead, **left** pad | Silk circle has its flat on the left |
| U1–U3 in sockets U1A–U3A | pin 1 bottom-left | Notch at the **left** end of the silk outline; socket first, IC pressed in |
| J2 1-641737-1 (or 350211-1) | pin 1 = +12 V, the square pad at the H1 end | **Component side** since 0.2.4 (0.2.x boards: solder side, pin 1 at the Q1 end); mating face toward the recessed rear edge; bench-check handedness first |
| F1, C1–C3, C6, R1–R21 | — | Non-polarized |

### Practical recommendation
Order the bare boards from JLCPCB (5 pcs, gold fingers, bevel). Assemble one yourself first — an hour —
and check the J2 hole size, Q1 orientation (gate in the square pad) and LED polarity before paying an
assembler for ten.
