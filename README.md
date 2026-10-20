# sa400-led-monitor — session workspace

Document: `README.md` · 2026-10-19 · board rev **v0.2.4** (J2 on the component side; not yet fabricated) — boards in hand are **v0.2.3**

Mirror of `C:\Users\ven\Desktop\Projects\_claude\sa400-led-monitor\`. Everything in `sa400_led_monitor/`
is also inside `sa400_led_monitor_v0.2.4.zip`.

## GitHub

Public repo: https://github.com/xtracool/trs80-m1-drive-monitor — the **TRS-80 Model I / Shugart drive monitor**
(a.k.a. TRS-80/Shugart drive monitor project). First commit 2026-10-19 = snapshot of the desktop folder at v0.2.4
(design) / test plan v1.4.

Not in git (see `.gitignore`): the packaged project/handoff zips, `_superseded/`, KiCad `.kicad_prl`. The JLCPCB
order number is masked in the committed copies of the reply notes.

### Working rules for Claude sessions (design and testing)
- **Pull before you start, push when you stop.** The repo is the hand-off point between sessions, not the desktop folder.
- One session edits a given area at a time. Testing session owns `docs/TEST_PLAN.md`, `pdf/build_test_plan.py`,
  `pdf/schematic.tex`, `pdf/fixtures.tex`, `gen/render_populated.py`, `docs/img/`; the design session owns the rest.
- Commit messages: `vX.Y.Z: <what>` for design releases, `testplan vN.M: <what>` for test-plan changes.
- `gen/verify.py` must exit 0 before any design commit that touches `gen/` or `kicad/`.

## Layout

| Path | What it is |
|---|---|
| `jlcpcb_v0.2.4/` | **Next fab set (J2 on top).** Gerber zip, BOM (J2 LCSC blank: consign 1-641737-1 or match C305826 for the vertical header), CPL (all 45 rows Top), render. Do not order until the J2 handedness bench check on the 0.2.3 boards is done (`sa400_led_monitor/docs/ASSEMBLY.md`). |
| `jlcpcb_v0.2.3/` | The set the boards in hand were made from: gerber zip, BOM/CPL, the 2026-10-07 orientation reply to JLCPCB (`jlcpcb_reply_email.txt`, `jlcpcb_orientation_reply.png`, `JLCPCB_REPLY_EMAIL.md`). |
| `jlcpcb_v0.2.2/` | What the current order (SMT0261xxxxxxx (order no. kept off GitHub)) was placed with on 2026-10-05: r2 BOM/CPL, remark, upload guide. Keep for reference. |
| `sa400_led_monitor_design_v0.2.4.pdf` | Full design document, 41 pages, footer on every page; carries the 2026-10-19 design-review corrections (red). |
| `sa400_led_monitor_test_plan_v1.x.pdf` | Bring-up test plan from the testing session (source `sa400_led_monitor/docs/TEST_PLAN.md`, built by `pdf/build_test_plan.py`). |
| `sa400_led_monitor/kicad/` | KiCad 10 project — open `sa400_led_monitor.kicad_pro`. |
| `sa400_led_monitor/gen/` | Python generator (`config.py` is the single source of truth, VERSION = "0.2.4"); `verify.py` release gate; **new** `outputs.py` makes the renders/copper views/STEP/schematic PDF. |
| `sa400_led_monitor/docs/` | THEORY_OF_OPERATION, BOM, MECHANICAL, CABLE, FABRICATION, ASSEMBLY (polarity table), TODO, CHANGELOG, V0.3_PLAN. |
| `sa400_led_monitor/output/` | Gerbers + upload zip, assembly BOM/CPL, DRC/ERC JSON, renders, STEP, schematic PDF. |
| `sa400_led_monitor/pdf/` | LuaLaTeX source (`template.tex`, `build_pdf.py`). |
| `sa400_led_monitor_v0.2.4.zip` | The project as a package. |
| `_superseded/` | v0.2.2 and v0.2.3 packages. |

## What v0.2.4 changed (details in `docs/CHANGELOG.md`)

- J2 moved to the **component side** as a right-angle Commercial Mate-N-Lok header (TE 1-641737-1; vertical
  350211-1 fits the same pads), mating face at the rear edge. JLCPCB's Economic PCBA is single-sided, which is
  why the 0.2.3 boards came back without J2. Pin 1 is now at the H1 end (mirror of the solder-side layout) —
  header handedness is still ASSUMED; bench check before soldering any header (ASSEMBLY.md).
- Power row moved down 2.54 mm for the J2 labels; copper re-routed; DRC/ERC/links clean.
- Merged the testing session's 2026-10-19 doc work (TEST_PLAN.md, design-review corrections in THEORY §3.0/§4.2/§4.3,
  V0.3_PLAN carry-overs F1–F4, render_populated.py, schematic.tex) so both lines of work live in one tree.

## What v0.2.3 changed

- Q1 TO-220 silkscreen redrawn to the real geometry (body over the pins, TAB band toward J2, G/D/S labels).
  JLCPCB's 3D render of v0.2.2 was already correct; only our silk box was on the wrong side.
- Schematic/BOM carry the as-built parts: R1–R8, R21 = 470 Ω; R19 = 2k2; Q1 = IRF4905PBF; LCSC numbers in
  the JLCPCB BOM; sockets as U1A/U2A/U3A with CPL rows. Theory of operation: +5 V budget ≈ 45 mA.
- Copper, mask, drills, outline: identical to v0.2.2 (every layer rendered with gerbv and diffed pixel-wise).

## Rebuild (Windows, KiCad 10.0.x)

```powershell
cd sa400_led_monitor
python gen\verify.py  --kicad-bin "C:/Program Files/KiCad/10.0/bin"   # gate + gerbers + BOM/CPL + upload zip
python gen\outputs.py --kicad-bin "C:/Program Files/KiCad/10.0/bin"   # renders, copper views, STEP, schematic PDF
python pdf\build_pdf.py                                                # design PDF (LuaLaTeX + fontspec/circuitikz)
```

Exit 0 = clean; 1 = a gate failed (message says which); 130 = interrupted.

## Status (2026-10-19)

- 0.2.3 boards received (5, populated except J2); testing in a separate session.
- 0.2.4 designed, verified, not ordered.

## TODO

- [ ] **J2 handedness bench check on a 0.2.3 board** (header in holes, plug on, yellow wire → `+12V` pad); fit the header on whichever side passes. Feed the result into `gen/config.py` (`J2_PIN1_X`, `J2_PIN_DIR`) before ordering 0.2.4.
- [ ] Measure the three ASSUMED dimensions (`J1_TAB_CORNER_GAP`, `J1_KEY_SLOT_W`, `J2_DRILL`) on the 0.2.3 boards.
- [ ] First power-up without the ribbon: D12, D13 lit, 5.0 V on any IC pin 14 — then the test plan.
- [ ] v0.3 (LED-bar modules, 74HCT244 per drive) — `sa400_led_monitor/docs/V0.3_PLAN.md`; J2 stays on the component side.
