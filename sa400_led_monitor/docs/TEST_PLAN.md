# Test Plan — SA400 Drive-Select / Write-Gate LED Monitor

Document: `TEST_PLAN.md` · Project: `sa400_led_monitor` · Test-plan version **1.4** · created 2026-10-19 · updated 2026-10-19

Revisions: 1.1 populated-board drawing and legend · 1.2 design-review findings folded in (§0.7, 2.6.17, 2.7.2, 2.7.4, 3.2.5, 3.3.7, §4, §5.3) · 1.3 drawings moved to appendices — A.1 board wireframe, A.2 legend, B schematic, C parts list — each on its own sheet (blank back) for double-sided printing · 1.4 Appendix D test-fixture drawings (jig, power pigtail, key plug) and Appendix E cable drawing

Colour key: <span style="color:#b00000">**red** = a stop condition, a limit not to exceed, or a correction to an earlier document</span> · <span style="color:#0040a0">**blue** = new or changed in revision 1.2 (the 2026-10-19 design review)</span>

Applies to: board rev **v0.2.2** copper (the 0.2.3 gerber changed Q1 silkscreen only), populated by JLCPCB
from the **r2** BOM/CPL in `jlcpcb_v0.2.2/`.

---

## 0. Read this first

### 0.1 What the three phases prove

| Phase | Setup | What it proves | Can it damage the TRS-80? |
|---|---|---|---|
| **1 — Unpowered** | Board only, DMM only | Assembly is right (orientation, values, no shorts); the bus fingers connect only where the design says | No — nothing is powered |
| **2 — Bench power** | Board + current-limited bench supply + a simple bus-simulator jig | Logic and LEDs work; the protection works; the **most** current and voltage the board can ever put on a bus line, measured | No — the EI and drives are not connected |
| **3 — On the EI** | Board on the real cable with the Expansion Interface, then with drives | Works with real signals; does not disturb disk I/O; safe in every power-on/power-off order | Only if a Phase 1 or 2 check was skipped or failed |

### 0.2 Rules

1. **Do the phases in order, on each board.** A board does not go to the next phase until every check in the
   current phase passes.
2. **Stop on the first out-of-spec reading.** Power off, write it down, and fix or diagnose before
   going on. Do not "see if it works anyway" with the EI attached.
3. **Never plug or unplug the card edge (J1) with anything powered.** Power (J2) may be unplugged while
   running only in step 3.5, which is designed for it.
4. **Board 1 goes all the way through first.** Boards 2–5 do Phase 1 and Phase 2 sections 2.1–2.6. Only board 1
   does the protection tests in 2.7 and 2.8 (they stress parts on purpose).
5. Write a serial number (1–5) on each board's silkscreen with a marker, and record results in the sheets
   in section 5.

### 0.3 As-built values (r2 BOM): these differ from older docs

`docs/BOM.md` and `THEORY_OF_OPERATION.md` still show the design-time values. The boards were built from
the r2 BOM, so **this plan uses the r2 values**:

| Ref | Design docs say | **As built (r2)** | Effect on readings |
|---|---|---|---|
| R1–R8 (drive LEDs), R21 (5V LED) | 1.5 kΩ | **470 Ω** | LEDs run ≈ 5.5–6.5 mA (still inside the 74LS00's 8 mA sink rating) |
| R19 (12V LED) | 4.7 kΩ | **2.2 kΩ** | D12 runs ≈ 4.5 mA |
| Q1 | NDP6020P | **IRF4905PBF** (same G-D-S pinout) | Specified for V_GS = −10 V; at our −5 V it should still be fully on at 35 mA, and **step 2.3 measures that** |
| R9–R13, R14–R18 | 10 kΩ, 470 Ω | same | — |

### 0.4 Reference map (used throughout)

**J1 card edge.** Even pins are on the component side, odd pins on the solder side directly underneath.

| Signal | J1 pin | Its GND partner (under it) | Series R (finger → receiver) | Pull-up | U1 input | U1 output | Red LED / driver | Green LED / driver |
|---|---|---|---|---|---|---|---|---|
| DS1 (TRS-80 drive :0) | 10 | 9 | R17 | R9 | U1-1 | U1-2 | D1 / U3-2 | D5 / U2-3 |
| DS2 (drive :1) | 12 | 11 | R16 | R10 | U1-3 | U1-4 | D2 / U3-4 | D6 / U2-6 |
| DS3 (drive :2) | 14 | 13 | R15 | R11 | U1-5 | U1-6 | D3 / U3-6 | D7 / U2-8 |
| DS4 (drive :3) | 6 | 5 | R18 | R12 | U1-9 | U1-8 | D4 / U3-8 | D8 / U2-11 |
| WRITE GATE | 24 | 23 | R14 | R13 | U1-11 | U1-10 | — | (all greens through U2) |

- **GND fingers (15):** 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31.
- **No-connect fingers (14):** 1 and 33 (they sit over the clip holes), and 2, 4, 8, 16, 18, 20, 22, 26, 28, 30, 32, 34.

**J2 power (Mate-N-Lok, solder side, pin 1 = square pad).** 1 = +12 V, 2 = +12 RTN, 3 = +5 RTN, 4 = +5 V.
This is the same connector and pinout as a PC "Molex" 4-pin peripheral plug (yellow +12, black, black, red +5).

**Power path.** J2-4 → F1 (PTC) → Q1 pin 2 (drain) → Q1 pin 3 (source) = **+5V rail** (also U1/U2/U3 pin 14,
D11 cathode, C4+). Q1 pin 1 (gate) = GND. J2-1 → R19 → D12 → GND only.

**Handy test points.** The vertical resistors stand up with one lead looped over the top. That loop is a
good probe point, but which net it is on depends on which way JLCPCB stood the part up. **Before you use any
resistor loop as a test point, check it with the DMM against the finger or the IC pin.**

### 0.5 Equipment

| Item | Needed for | Notes |
|---|---|---|
| DMM with ohms, diode, DC volts, DC mA | all | A second DMM to watch current while you probe saves time |
| Bench supply, adjustable 0–15 V, **adjustable current limit** | 2, 3 | Two outputs is ideal (one for the board, one for the jig pull-ups). The outputs must be floating (not tied to earth on +) |
| Power pigtail for J2 (drawing: Appendix D.2) | 2, 3 | TE/AMP 1-480424-0 housing + 60619-1 pins — https://www.te.com/en/product-1-480424-0.html · pins https://www.mouser.com/c/?q=60619-1 — or any PC Molex-to-bare-wire cable (same connector). Label the wires. |
| **Bus-simulator jig** (section 0.6, drawing: Appendix D.1) | 2 | Recommended. The fallback is clip leads on the fingers, which risks scratching the gold or bridging two fingers |
| IC extractor, ESD strap | 1, 2.7, 2.8 | ICs are socketed, so you can pull them for the protection tests |
| Scope (optional) | 3.3 | Best way to show the board doesn't change bus levels or edges |
| IR thermometer or fingertip | 2, 3.6 | Heat check |
| Scratch diskettes (2+) | 3 | **Never test writes on a disk you care about** |

### 0.6 Bus-simulator jig ("fake EI")

Drawing: **Appendix D.1**. Power pigtail: **D.2**. Key plug: **D.3**. Cable for Phase 3: **Appendix E**.

This stands in for the EI's open-collector drivers and the terminating drive. Each line is held high by
150 Ω (like the terminator), and a switch pulls it to ground (like a 7438 asserting the line).

```
 3M 3463-0001 card-edge IDC  --  ~150 mm 34-way ribbon  --  cut end; separate:
   (red stripe = pin 1)            signals : 6, 10, 12, 14, 24
                                   GND     : 5, 9, 11, 13, 23 (twist together)

 Each signal conductor (x5):

   +5V_JIG --[JP on/off]--[150 R]--+-- conductor 6 / 10 / 12 / 14 / 24
                                   |
                                 [SW n]   closed = ASSERTED
                                   |
                                  GND --- GND conductors + bench supply (-)
```

- Use a 3463-0001 from the cable build: https://www.mouser.com/c/?q=3463-0001
- Ribbon conductor N = J1 pin N when the stripe is on pin 1 of the IDC connector. Before you trust the jig,
  check that with the DMM.
- **JP** turns the five 150 Ω pull-ups on or off. *Off* = the board's own 10 k pull-ups only. *On* =
  simulates a terminated bus. +5V_JIG comes from the second bench output (or the same output, but then the
  board-current reading also includes the jig current).
- Five switches, labelled DS1 DS2 DS3 DS4 WG.

### 0.7 Design-review findings (2026-10-19) and where each one is tested

<span style="color:#0040a0">Added in 1.2. A review of the v0.2.2 design against the datasheets found one real margin issue (F1) and
three smaller points. None of them stops the test run; each is tied to a step below.</span>

| # | Finding | Tested at | What to do |
|--|------------------------------------------|----------|------------------------|
| F1 | <span style="color:#0040a0">**Receiver low-level margin.** When a bus line is low, the LS14 input current (0.4 mA max) *and* the R9–R13 pull-up current (≈ 0.44 mA) both flow out through the 470 Ω series resistor. Worst case the U1 input sits at ≈ 0.79 V (0.4 V VOL + 0.84 mA × 470 Ω) against a 74LS14 VT− of 0.5 V min / 0.8 V typ / 1.0 V max. Typical parts give ≈ 0.55 V, so it works on typical margin.</span> <span style="color:#b00000">THEORY §3.0's 0.59 V figure left out the pull-up term; corrected there.</span> | **3.3.7** (the number that matters), 3.2.5, 2.6.17 | If 3.3.7 reads > 0.5 V: fit a **74HCT14** in U1's socket (no soldering; input current is µA, which removes ≈ 0.19 V). Optionally R9–R13 → 47–100 k (removes most of the other ≈ 0.2 V). v0.3: pull-ups move to the finger side of R14–R18 (V0.3_PLAN). |
| F2 | <span style="color:#0040a0">**+12 V on the +5 V pin** is harsher than THEORY §4.3 said. A cold 0.5 A PTC is ≈ 0.5 Ω, so until F1 trips D11 takes whatever the supply will deliver at ≈ 6 V. F1 trips and the EI never sees it, but D11 may fail (normally short: board dead, still safe).</span> | 2.7.4 | Stays optional. <span style="color:#b00000">Expect to lose D11 if you run it from a stiff supply.</span> The Mate-N-Lok is keyed; this fault needs a hand-made cable. |
| F3 | <span style="color:#0040a0">**D12 reverse rating.** Reversed +12 V puts ≈ 7 V reverse across D12 (5 mm LEDs are rated ≈ 5 V) at ≈ 3 mA through R19. Likely survives, but out of spec.</span> | 2.7.2 | Run it knowing that, or skip it. v0.3: 1N4148 in series with D12. |
| F4 | <span style="color:#0040a0">Minor: D11 (5.6 V, soft knee) leaks a few mA at 5.25 V and runs slightly warm; U2 sinks ≈ 5.3 mA per green LED with the as-built 470 Ω (LS00 rating 8 mA); IRF4905 at V_GS = −5 V.</span> | 2.4.2, 2.6.20, 2.3 | Record. The 74LS37 is a pin-compatible 24 mA drop-in for U2 if brighter greens are wanted later. |

Checked in the same review and found right: Q1's orientation (drain in, source out, gate to ground is the
correct way round for a P-channel reverse-polarity switch), all unused inputs tied, no path from +12 V to
either the rail or the bus, ≤ 12 mA worst case into an EI line, no termination, the LS06 for the reds,
and U1's fan-out.

---

## Phase 1 — Unpowered (no supply, not on the EI)

Board fully assembled, ICs in their sockets, nothing plugged into J1 or J2. Hold the DMM leads still while
a reading settles, because the capacitors charge through the meter.

### 1.1 Visual and mechanical

| # | Check | Pass |
|---|---|---|
| 1.1.1 | U1 = 74LS14, U2 = 74LS00, U3 = 74LS06, each in the correct position, notch matches the silk, every pin inside the socket (none folded under) | ✓ |
| 1.1.2 | Q1 is the IRF4905: pin 1 (gate) in the square pad, metal tab on the side shown by the silkscreen | ✓ |
| 1.1.3 | D11: band (cathode) at the square pad. C4: + lead at the square pad | ✓ |
| 1.1.4 | All LEDs: flat side / short lead (cathode) at the square pad. Colours: D1–D4 red, D5–D8 green, D12–D13 yellow | ✓ |
| 1.1.5 | Resistor colour bands: R1–R8, R21, R14–R18 = 470 Ω (yellow-violet-brown); R9–R13 = 10 k (brown-black-orange); R19 = 2.2 k (red-red-black-brown for 1 %) | ✓ |
| 1.1.6 | J2 is on the **solder side**, housing opening toward the rear edge, seated flat | ✓ |
| 1.1.7 | Solder side: no bridges, especially across the J2 pins and the DIP rows. No flux balls | ✓ |
| 1.1.8 | Fingers: gold, bevelled, **no solder or flux on any finger**, no lifted finger | ✓ |
| 1.1.9 | Board thickness at the fingers (calipers): 1.37–1.78 mm (3M spec), expect 1.6 | record |
| 1.1.10 | Fit test: push a **bare** 3463 connector (not on a live cable) onto the tab. It seats fully, and the key (if fitted) goes into the slot between pins 4 and 6. Remove it | ✓ |
| 1.1.11 | Fit test: the power plug latches into J2 and only goes in one way | ✓ |
| 1.1.12 | **Record the three ASSUMED dimensions** while you have calipers out: tab edge to corner (5.08 assumed), key-plug width (0.91), J2 pin drill (2.1) — see `docs/MECHANICAL.md` | record |

### 1.2 Power connector — no shorts between rails

DMM in ohms unless stated. "OL" = open / over-range.

| # | From (red) | To (black) | Expect | Proves |
|---|---|---|---|---|
| 1.2.1 | J2-1 (+12) | J2-4 (+5) | **OL**, then try the leads the other way: **OL** | 12 V can never reach the 5 V rail through the board |
| 1.2.2 | J2-2 | J2-3 | < 1 Ω | Both returns are tied together |
| 1.2.3 | J2-3 | J1-9 (any GND finger) | < 1 Ω | Supply ground = bus ground |
| 1.2.4 | J2-4 | J2-3 (GND) | > 200 Ω and settling (not a dead short) | No short across the +5 V input |
| 1.2.5 | J2-1 | J2-3 | > 2 kΩ or OL | No short across the +12 V input |
| 1.2.6 | J2-4 | F1 far lead / Q1 pin 2 | < 2 Ω (cold PTC) | F1 is in circuit and intact |
| 1.2.7 | Q1 pin 1 (gate) | GND | < 1 Ω | Gate tied to ground as designed |

### 1.3 Reverse-polarity switch (Q1) orientation — diode mode

| # | Red lead | Black lead | Expect | Proves |
|---|---|---|---|---|
| 1.3.1 | Q1 pin 2 (drain) | Q1 pin 3 (source / rail) | 0.4–0.7 V | Body diode points from input to rail, so Q1 is fitted the right way round |
| 1.3.2 | Q1 pin 3 | Q1 pin 2 | OL (may start low and climb while C4 charges) | Reversed supply will be blocked |
| 1.3.3 | J2-4 | U1-14 (+5V rail) | 0.4–0.7 V | Whole input path F1 → Q1 → rail is in one piece |
| 1.3.4 | GND | U1-14 | 0.4–0.8 V | Normal: D11 and the IC substrate diodes. **≈ 0 V = short on the rail** |

If 1.3.1 reads OL and 1.3.2 reads 0.5 V, Q1 is in backwards. **Stop.**

### 1.4 Bus fingers — the board touches only what it should

This is the core "cannot hurt the EI" check with no power applied.

| # | Test | Expect |
|---|---|---|
| 1.4.1 | Each of the **14 no-connect fingers** (1, 33, 2, 4, 8, 16, 18, 20, 22, 26, 28, 30, 32, 34) to GND (J2-3) | **OL** |
| 1.4.2 | The same 14 fingers to the +5V rail (U1-14) | **OL** |
| 1.4.3 | Each of the **15 GND fingers** to J2-3 | < 1 Ω |
| 1.4.4 | Each monitored finger to its U1 input (table 0.4, e.g. J1-10 → U1-1) | **447–494 Ω** (470 Ω ±5 %) |
| 1.4.5 | Each monitored finger to the +5V rail, red lead on the finger | **9.9–11.0 kΩ** (470 Ω + 10 kΩ) |
| 1.4.6 | Each monitored finger to GND | > 10 kΩ, **never < 1 kΩ** |
| 1.4.7 | Adjacent signal fingers to each other: 10↔12, 12↔14, 4↔6, 6↔8, 22↔24, 24↔26 | ≈ 21 kΩ between two monitored fingers (each one's 10.47 k to the rail), **OL** when one of the pair is a no-connect |
| 1.4.8 | Each monitored finger and J2-1 (+12) | **OL** — 12 V has no path to the bus |

### 1.5 LEDs in circuit — diode mode

Red lead on the anode (round pad), black lead on the cathode (square pad). Most DMMs light a red or yellow
LED faintly. Some can't light green.

| # | LED | Expect |
|---|---|---|
| 1.5.1 | D1–D4, D12, D13 | 1.5–2.1 V, faint glow |
| 1.5.2 | D5–D8 | 1.7–2.4 V or OL (meter can't reach a green's Vf); faint glow if it can |
| 1.5.3 | Each LED reversed | OL or a much higher reading (other in-circuit paths) |

Phase 1 done → record, go to Phase 2.

---

## Phase 2 — Bench power, not on the EI

Board on the bench, J2 fed from the bench supply through the pigtail. J1 is either empty or plugged into
the **jig only**. The EI, drives and cable are nowhere near it.

Expected currents (as built):

| Condition | Expected +5 V current |
|---|---|
| Idle (no line asserted) | **≈ 25–45 mA** (three LS ICs + D13 at ≈ 6 mA) — accept 15–60 mA, but boards should agree within ±20 % |
| Each asserted line (jig pull-ups off) | + ≈ 0.48 mA (its 10.47 k pull-up path) + any LED it lights |
| One drive selected | + ≈ 5.5–6 mA (red) |
| Selected and writing | + another ≈ 5.5 mA (green) |
| +12 V input | ≈ 4.5 mA (D12 only) |

### 2.1 First power-up — +5 V only, current-limited

1. Supply output **off**. Set it to **0 V, 100 mA limit**. Connect J2-4 (+) and J2-3 (−). Leave J2-1 open.
   Nothing on J1.
2. Turn the output on and **raise slowly** to 5.00 V, watching the current.
   - Over 60 mA at any point, or the supply drops into current limit → **stop**: short, or a reversed IC.
3. At 5.00 V record:

| # | Measure | Expect |
|---|---|---|
| 2.1.1 | Supply current | 15–60 mA (record exactly — this is the board's fingerprint) |
| 2.1.2 | D13 "5V" | lit |
| 2.1.3 | D1–D8, D12 | **all off** (no line asserted; D12 has no +12 V) |
| 2.1.4 | Touch test after 1 min: U1–U3, Q1, D11, F1 | none warm |

### 2.2 Rail voltages

| # | Measure (black on GND) | Expect |
|---|---|---|
| 2.2.1 | J2-4 | 5.00 V (set) |
| 2.2.2 | +5V rail at U1-14, U2-14, U3-14 | within 0.05 V of J2-4 |
| 2.2.3 | U1-7, U2-7, U3-7 | 0.00 V |

### 2.3 Q1 voltage drop

| # | Measure | Expect | If not |
|---|---|---|---|
| 2.3.1 | DC volts, red J2-4, black U1-14 | **< 0.05 V** | 0.4–0.7 V means Q1's channel is not turning on and the current is going through its body diode. The rail would then sit around 4.4 V, below the 74LS minimum of 4.75 V. Check Q1 orientation and part; the IRF4905 should be fully on at −5 V V_GS for 35 mA |

### 2.4 Supply tolerance and clamp leakage

| # | Set J2-4 to | Measure | Expect |
|---|---|---|---|
| 2.4.1 | 4.75 V | current; then repeat 2.5 for one drive | LEDs still work |
| 2.4.2 | 5.25 V | current | No more than **5 mA** above the 5.00 V reading. A bigger rise means D11 (5.32 V minimum knee) is starting to conduct; record it |
| 2.4.3 | back to 5.00 V | — | — |

### 2.5 +12 V indicator

1. Second output (or the same supply in a second step): 12.0 V, **50 mA limit**, J2-1 (+) / J2-2 (−).

| # | Measure | Expect |
|---|---|---|
| 2.5.1 | +12 V current | 3.5–5.5 mA |
| 2.5.2 | D12 "12V" | lit |
| 2.5.3 | +5V rail (U1-14) | unchanged from 2.2 — 12 V does not leak onto the logic |
| 2.5.4 | Every monitored finger (6, 10, 12, 14, 24), open circuit | ≈ +5 V, **never above the rail** |

### 2.6 Bus isolation and logic — with the jig

The monitor stays at 5.00 V / 100 mA limit. Plug the **jig** (pull-ups **off**, all switches open) onto J1
with the board's supply **off**, then power up.

**2.6.A — What the board puts on the bus (the "will it short the EI or a drive" numbers)**

| # | Test | Expect | Proves |
|---|---|---|---|
| 2.6.1 | DC volts, each monitored line to GND, all switches open | 4.8–5.25 V (the rail through 10.47 k) | The board only ever *pulls up weakly*; it never drives a line |
| 2.6.2 | DC **mA** meter from each monitored line to GND (meter in place of the switch) | **0.45–0.55 mA** | The **most** current the board can push into a bus line in normal operation: < 2 % of the 31 mA the terminator already makes the EI sink |
| 2.6.3 | DC volts, each **no-connect** finger to GND (probe the ribbon conductor) | 0.00 V (floating) | The board leaves the other 12 signals alone |
| 2.6.4 | Board supply current with all five switches closed (lines held low), no LEDs counted | idle + 5 × 0.48 ≈ idle + 2.4 mA (plus the LEDs that light) | Matches the pull-up model |

**2.6.B — Logic truth table** (jig pull-ups off, then repeat with them **on**)

| # | Switches closed | Expect lit | Must stay dark |
|---|---|---|---|
| 2.6.5 | none | D13 | D1–D8 |
| 2.6.6 | DS1 | D1 | all other drive LEDs |
| 2.6.7 | DS2 | D2 | " |
| 2.6.8 | DS3 | D3 | " |
| 2.6.9 | DS4 | D4 | " |
| 2.6.10 | WG only | none | D1–D8 (write gate with no drive selected lights nothing) |
| 2.6.11 | DS1 + WG | D1 + D5 | others |
| 2.6.12 | DS2 + WG | D2 + D6 | others |
| 2.6.13 | DS3 + WG | D3 + D7 | others |
| 2.6.14 | DS4 + WG | D4 + D8 | others |
| 2.6.15 | DS1 + DS3 (two selects, not legal on a real bus) | D1 + D3 | — shows the channels are independent |

**2.6.C — Levels** (one channel, DS1 + WG closed, jig pull-ups **on**)

| # | Measure | Expect |
|---|---|---|
| 2.6.16 | J1-10 (finger) | ≈ 0 V (switch) |
| 2.6.17 | U1-1 (receiver input, after R17) | <span style="color:#0040a0">**< 0.45 V** (1.2: was 0.4 V. A hard ground on the jig gives ≈ 0.31 V typical, 0.40 V worst case: F1)</span> |
| 2.6.18 | U1-2 (DS1, active-high) | > 2.7 V |
| 2.6.19 | U3-2 (red cathode) / U2-3 (green cathode) | < 0.5 V each |
| 2.6.20 | Voltage across R1 (red D1 resistor) | 2.5–2.9 V → ≈ 5.3–6.2 mA |
| 2.6.21 | Switch open again: U1-1 | > 4.5 V; U1-2 < 0.5 V; LEDs off |

If a channel fails, follow it down that row of table 0.4: finger → series R → U1 input → U1 output → U3/U2
output → LED. The first stage that reads wrong is the fault.

**2.6.D — Unpowered board on a powered bus** (EI on, monitor off — the reverse case)

| # | Test | Expect |
|---|---|---|
| 2.6.22 | Board supply **disconnected** from J2. Jig pull-ups **on** (+5V_JIG = 5.0 V). mA meter in series with one 150 Ω pull-up → line | Line current changes by **< 0.6 mA** between the board plugged in and the board off the jig |
| 2.6.23 | With all five pull-ups on, measure the dead board's +5V rail (U1-14) | Record. Expect well under 2 V; D13 may glow very faintly. The back-feed is limited by 470 Ω + 10 kΩ per line |
| 2.6.24 | Line high voltage at the jig with the dead board plugged in | ≥ 4.9 V (the board doesn't drag the bus down when it's unpowered) |

### 2.7 Protection tests — **board 1 only**

These deliberately apply the faults in `THEORY_OF_OPERATION.md` §4.3. **Pull U1, U2 and U3 from their
sockets first** (note the orientation) so an unexpected result can only cost a cheap part. Jig disconnected.

| # | Fault applied | How | Expect | Pass |
|---|---|---|---|---|
| 2.7.1 | **Reversed +5 V** | 5.0 V, 50 mA limit, **+ on J2-3, − on J2-4** | Current < 1 mA; rail (U1 socket pin 14 to GND) ≈ 0 V; D13 dark | Q1 blocks |
| 2.7.2 | **Reversed +12 V** | 12 V, 50 mA limit, + on J2-2, − on J2-1 | Current ≈ 3 mA (D12 in reverse breakdown through R19); D12 dark | Nothing else conducts. <span style="color:#b00000">Puts D12 ≈ 2 V past its reverse rating (F3). Likely survives; skip if you'd rather not.</span> |
| 2.7.3 | **Overvoltage on +5 V** (clamp) | Normal polarity, **300 mA limit**. Raise J2-4 from 5.0 V in 0.2 V steps to 7.0 V or until the supply hits its limit. At each step record the input V, the current and the rail V | Rail follows the input up to D11's knee (≈ 5.3–5.9 V); after that the current climbs steeply while the rail rises slowly | Rail **< 6.5 V** at 300 mA (74LS absolute max is 7.0 V). Don't hold more than 30 s at 300 mA |
| 2.7.4 | *Optional* — **12 V on the +5 V pin** (miswired cable) | Normal polarity, **12 V, 2 A limit**, ICs still out. Watch the current; switch off after 10 s regardless | <span style="color:#b00000">Current goes straight to the supply's 2 A limit (the cold PTC is ≈ 0.5 Ω; it does not limit anything), D11 dissipates ≈ 12 W until F1 trips, well under a second; then the current falls to tens of mA. Rail stays < 7 V throughout.</span> Let it cool 5 min, then repeat 2.1 → normal | F1 trips; nothing smokes. <span style="color:#b00000">D11 may fail short (F2): then the rail reads ≈ 0 V and D11 must be replaced before 2.1 passes.</span> |

<span style="color:#b00000">Skip 2.7.4 unless you are willing to lose D11. From a 2 A bench limit it will probably survive the pulse; from a PC
supply (tens of amps) it would not. Steps 2.7.1–2.7.3 already show the clamp and the reverse block work.</span>

### 2.8 Worst-case fault current into a bus line — **board 1 only**

This checks the worst case the 470 Ω series resistors are there for: a dead receiver shorting a bus line to the rail.

1. ICs **out**. Board at 5.00 V, 100 mA limit.
2. Jumper **U1 socket pin 1 (DS1_in) to U1 socket pin 14 (+5 V)**. This simulates a receiver input welded
   to the rail.
3. mA meter from **J1-10** (finger) to **GND**.

| # | Expect | Pass |
|---|---|---|
| 2.8.1 | ≈ 10.6 mA (5.0 V / 470 Ω) | **≤ 12 mA** — added to the terminator's 31 mA, that's 43 mA, inside the 7438's 48 mA rating |

Repeat for one more channel (e.g. U1 pin 11 / J1-24). Remove the jumper, refit the ICs (check the notches),
and re-run 2.1 and 2.6.B quickly.

Phase 2 done → record, go to Phase 3 (board 1 first).

---

## Phase 3 — On the Expansion Interface

### 3.0 Before starting

- [ ] Board has passed Phase 1 and Phase 2.
- [ ] **Baseline without the monitor:** Model I + EI + drives boot DOS, `DIR` each drive, read a few files.
      Write down anything that already misbehaves, so it isn't blamed on the monitor later.
- [ ] **Cable.** Use the six-connector cable from `docs/CABLE.md` (drawing: Appendix E), or a straight-through cable with a spare
      connector. **On a Radio Shack "pulled-pin" cable** each drive connector carries only one drive-select
      line, so the monitor would only ever see that one drive. Put it on a connector with all 34 contacts.
- [ ] Cable continuity: each connector, pin N to pin N, and no adjacent-pin shorts (DMM, 2 minutes).
- [ ] Red stripe = pin 1 on every connector. On the monitor, pin 1 is the solder-side finger directly
      under pin 2, at the **board-corner end of the tab, away from J2**. Confirm against the silk pin
      numbers before mating.
- [ ] The terminated drive is at the **far end** of the cable. The monitor adds no terminator.

### 3.1 Ground and supply check

1. Model I + EI **on**, cable connected to the EI but **not** to the monitor. Monitor supply on but not
   connected to the monitor.
2. DC volts between the **bench supply (−)** and the **EI chassis / a GND pin**: < 0.1 V. AC volts: < 0.1 V.
   - A higher reading means the bench supply or the EI is floating at a different potential. Connecting it
     through the cable's ground would push current through the ribbon. **Fix first** (bring both to the
     same mains ground, or use a floating supply).
3. Everything **off**.

### 3.2 Stage A — EI + monitor, no drives

1. Everything off. Plug the monitor onto the DIAG connector (stripe to pin 1). **No drives connected.**
2. Monitor supply: 5.00 V, 100 mA limit (+12 V optional). Power on → idle current same as 2.1.1 (± 2 mA).
3. Power on the Model I / EI.

| # | Observe | Expect |
|---|---|---|
| 3.2.1 | Monitor current as the EI powers up | stays within idle + 15 mA, no spike to the limit |
| 3.2.2 | At power-on, with no drive fitted | The ROM tries to boot drive :0, so **D1 should light** (DS1 asserted). Hold BREAK (or reset with BREAK) to get to BASIC |
| 3.2.3 | Run the select-cycling program below | D1 → D2 → D3 → D4 in turn, about 1 s each; **no green ever** |
| 3.2.4 | DMM on J1-10 side of R17 (or scope) while :0 selected | ≤ 0.4 V asserted, ≈ 5 V released |
| <span style="color:#0040a0">3.2.5 (1.2, F1)</span> | <span style="color:#0040a0">DMM on **U1-1** (the DS1 receiver input, after R17) while :0 is selected: hold BREAK at power-on, or the cycling program</span> | <span style="color:#0040a0">Record. With no drives there is no terminator, so the EI driver sinks almost nothing and this reads low, ≈ 0.3–0.4 V. The number that matters is 3.3.7.</span> |

```basic
10 REM CYCLE DRIVE SELECTS :0-:3, 37E1H = 14305 (MODEL I DRIVE SELECT LATCH)
20 FOR D = 0 TO 3
30 V = 2 ^ D
40 FOR T = 1 TO 150 : POKE 14305, V : NEXT T
50 NEXT D
60 GOTO 20
```

The EI's select latch is cleared by the motor-on timeout after a few seconds, which is why line 40 keeps
re-writing it. Without drives there's no terminator, so the monitor's 10 k pull-ups are the only thing
pulling the lines high. That's fine for this test.

### 3.3 Stage B — EI + monitor + drives

1. Everything off. Connect the drives (terminated drive at the end). Monitor on DIAG.
2. Power order: monitor supply → drives → Model I / EI.

| # | Test | Expect |
|---|---|---|
| 3.3.1 | Boot DOS from :0 | Boots exactly as in the baseline. D1 lights whenever drive :0's own activity LED does |
| 3.3.2 | `DIR` on each drive present | Red LED for that drive only, in step with the drive's own LED |
| 3.3.3 | Run the BASIC select-cycling program (from Disk BASIC) | As 3.2.3; the drive motors start, which is normal |
| 3.3.4 | **Write test** — scratch disk in :1. Save a file or format it (syntax depends on the DOS) | D2 red throughout, **D6 green only while writing**. No green on any other drive |
| 3.3.5 | Read back / `DIR` the scratch disk; copy a file :0 → :1 and compare | No errors, same as the baseline |
| 3.3.6 | *(scope, optional)* DS1 at the DIAG connector, monitor plugged in vs removed (everything off to swap) | Low level differs by < 50 mV; rise and fall times look the same |
| <span style="color:#0040a0">3.3.7 (1.2, F1)</span> | <span style="color:#0040a0">**Receiver margin.** With the drives connected (terminated bus), DMM on **U1-1** while :0 is selected (repeated `DIR :0`, or the cycling program). Also U1-3 / U1-5 / U1-9 for :1 / :2 / :3 if those drives are fitted. Note the finger voltage (J1-10) alongside for comparison.</span> | <span style="color:#0040a0">**≤ 0.50 V = clean** (below the 74LS14's minimum VT−). **0.50–0.80 V = works on typical margin**: fit a 74HCT14 in U1 (and optionally 47–100 k for R9–R13), re-measure; each change should drop the reading by ≈ 0.2 V.</span> <span style="color:#b00000">**> 0.80 V = a select can be missed.** Do not rely on the board until U1 is swapped and the reading is ≤ 0.8 V.</span> |

### 3.4 Power-order robustness

Run a read loop (e.g. repeated `DIR :0`, or a BASIC program that LOADs a file over and over) and, **without
touching the card edge**:

| # | Action | Expect |
|---|---|---|
| 3.4.1 | Unplug the monitor's **J2** (power) while the loop runs | Loop continues with no errors; monitor LEDs go dark |
| 3.4.2 | Plug J2 back in | Loop continues; LEDs resume |
| 3.4.3 | Monitor powered, Model I / EI and drives off | Monitor current back to idle; no LEDs except D13 (and D12) |
| 3.4.4 | Monitor unpowered, power the system on and boot | Boots normally (an unpowered monitor doesn't load the bus) |

### 3.5 Soak

| # | Test | Expect |
|---|---|---|
| 3.5.1 | 1 hour of mixed read/write on a scratch disk | No disk errors beyond the baseline |
| 3.5.2 | Heat check at the end: U1–U3, Q1, D11, F1, R1–R8 | All barely warm (< 45 °C). **D11 warm** means the rail is above its knee: check the supply voltage |
| 3.5.3 | Monitor current at the end | Same as at the start (± 2 mA) |

### 3.6 Final power source

If the monitor will normally be powered from something other than the bench supply (a PC PSU Molex lead,
a drive's supply), repeat **2.1–2.2** on that source with a meter in series (expect 4.75–5.25 V at J2-4),
then **3.3.1–3.3.4** briefly.

---

## 4. If something fails

| Symptom | Most likely | Look at |
|---|---|---|
| Current at the limit on first power-up | Reversed IC, solder bridge, C4 reversed | 1.1.1, 1.1.3, 1.3.4 |
| Rail ≈ 0.5 V below J2-4 | Q1 conducting only through its body diode | 2.3, Q1 orientation / part |
| All LEDs dead, D13 lit | U1 missing/reversed, or the fingers not making contact | U1-14 voltage, 2.6.C |
| One red never lights | That row of table 0.4 | Series R, pull-up, U1 gate, U3 gate, LED polarity |
| Red lights but its green never does | That U2 gate, its LED, or WG path (R14, U1-11/10) | 2.6.C |
| Green lights with its red even when not writing | WG stuck active: U1-11 shorted to GND, or U1 gate 5 faulty | U1-11 should be > 4.5 V with WG released; U1-10 < 0.5 V |
| Green never lights on any drive | WG path open: R14, or U1-11/U1-10 | 2.6.C on the WG row |
| LEDs flicker with nothing asserted | Pull-up open, so a floating LS14 input | R9–R13 |
| <span style="color:#0040a0">A drive's red is erratic or misses short accesses that the drive's own LED shows</span> | <span style="color:#0040a0">Receiver margin (F1): U1 input node too high</span> | <span style="color:#0040a0">3.3.7; 74HCT14 in U1</span> |
| Disk errors with the monitor fitted but not without | Cable (the sixth connector), terminator position, or a monitored line loaded | 3.0 cable checks, 2.6.1–2.6.2 on that board, 3.3.6 |

---

## 5. Record sheets

Tick ✓ or write the reading. One column per board.

### 5.1 Phase 1

| Step | B1 | B2 | B3 | B4 | B5 |
|--------------------------------------------------|------|------|------|------|------|
| 1.1.1–1.1.8 visual | | | | | |
| 1.1.9 thickness (mm) | | | | | |
| 1.1.10–1.1.11 fit | | | | | |
| 1.1.12 tab-corner / key / J2 drill (mm) | | | | | |
| 1.2.1 +12↔+5 OL | | | | | |
| 1.2.4 J2-4↔GND (Ω) | | | | | |
| 1.2.6 F1 (Ω) | | | | | |
| 1.3.1 Q1 body diode (V) | | | | | |
| 1.3.4 GND↔rail diode (V) | | | | | |
| 1.4.1–1.4.2 no-connect fingers OL | | | | | |
| 1.4.3 GND fingers | | | | | |
| 1.4.4 series R (Ω) 10/12/14/6/24 | | | | | |
| 1.4.5 finger→rail (kΩ) 10/12/14/6/24 | | | | | |
| 1.4.8 fingers↔+12 OL | | | | | |
| 1.5 LEDs | | | | | |

### 5.2 Phase 2

| Step | B1 | B2 | B3 | B4 | B5 |
|--------------------------------------------------|------|------|------|------|------|
| 2.1.1 idle current (mA) | | | | | |
| 2.2.2 rail (V) | | | | | |
| 2.3.1 Q1 drop (V) | | | | | |
| 2.4.1 works at 4.75 V | | | | | |
| 2.4.2 current at 5.25 V (mA) | | | | | |
| 2.5.1 +12 current (mA) | | | | | |
| 2.6.1 line open V (min/max) | | | | | |
| 2.6.2 line short mA (max) | | | | | |
| 2.6.5–2.6.15 truth table, pull-ups off | | | | | |
| 2.6.5–2.6.15 truth table, pull-ups on | | | | | |
| 2.6.20 LED resistor V | | | | | |
| 2.6.22 dead-board line current (mA) | | | | | |
| 2.6.23 back-fed rail (V) | | | | | |
| 2.7.1 reverse +5 (mA) | | — | — | — | — |
| 2.7.3 rail at 300 mA (V) | | — | — | — | — |
| 2.7.4 PTC trip (optional) | | — | — | — | — |
| 2.8.1 fault current (mA) | | — | — | — | — |

### 5.3 Phase 3

| Step | B1 | B2 | B3 | B4 | B5 |
|--------------------------------------------------|------|------|------|------|------|
| 3.1 ground offset (V DC / AC) | | | | | |
| 3.2.1–3.2.4 EI only | | | | | |
| <span style="color:#0040a0">3.2.5 U1-1, no drives (V)</span> | | | | | |
| 3.3.1–3.3.5 with drives | | | | | |
| <span style="color:#0040a0">3.3.7 U1-1, with drives (V) → HCT14?</span> | | | | | |
| 3.3.6 scope delta (mV) | | | | | |
| 3.4.1–3.4.4 power order | | | | | |
| 3.5 soak / heat / current | | | | | |
| 3.6 final supply | | | | | |

---

## 6. TODO

- [ ] Build the bus-simulator jig (0.6)
- [ ] Board 1: Phase 1 → Phase 2 (all, including 2.7/2.8) → Phase 3
- [ ] Boards 2–5: Phase 1 → Phase 2 (2.1–2.6) → Phase 3 (3.3.1–3.3.4)
- [ ] <span style="color:#0040a0">3.3.7 result → decide whether U1 becomes a 74HCT14 (F1); record which boards got it</span>
- [ ] Feed the 1.1.12 measurements into `gen/config.py` and close the ASSUMED items in `docs/MECHANICAL.md`
- [ ] Bring `docs/BOM.md` and `THEORY_OF_OPERATION.md` up to the r2 values (table 0.3)
- [ ] Results go into the v0.3 plan (`docs/V0.3_PLAN.md`)

---

## Appendix A — Board drawing

### A.1 Populated board, component side (wireframe)

![Populated board, component side, wireframe. Generated by `gen/render_populated.py` from the footprint positions in `gen/design.py`; values are the as-built r2 BOM. J1 fingers at the top, pin 2 at the right; J2 (dashed) is on the solder side.](img/board_populated.png){width=100%}

### A.2 Legend for A.1

| Ref | Part (as built, r2 BOM) | Drawn as | Job on the board | Check when inspecting |
|---|---|---|---|---|
| U1 | 74LS14 hex Schmitt inverter, DIP-14, in socket | Solid rounded box with end notch, inside a dashed socket outline | Bus receivers for DS1–DS4 and WRITE GATE | Notch at left; pin 1 = square pad, bottom-left |
| U2 | 74LS00 quad NAND, DIP-14, in socket | Same | Green LEDs: DSn AND WG | Same |
| U3 | 74LS06 hex open-collector inverter, DIP-14, in socket | Same | Red LEDs: DSn | Same |
| Q1 | IRF4905 P-channel MOSFET, TO-220, standing | Rectangle (body) + thin rectangle (metal tab), pins G D S | Reverse-polarity switch on +5 V | Gate in the square pad; tab toward the front edge |
| F1 | PTC resettable fuse 0.5 A | Rounded bar | +5 V input fuse | — |
| D11 | 1N5339B 5.6 V 5 W Zener, DO-15, standing | Double circle (body + band) with the lead down to the anode | +5 V rail clamp | Band (cathode) on top, in the square pad |
| C4 | 10 µF 16 V electrolytic | Circle with "+" and a line on the stripe side | Bulk +5 V | + lead in the square pad |
| C1, C2, C3, C6 | 100 nF ceramic disc | Small rounded slot | Decoupling U1/U2/U3; rail entry (C6) | — |
| R14–R18 | 470 Ω ¼ W, standing | Circle (body) + line (lead) | Bus series resistors, finger → receiver (fault-current limit) | Value printed under the lead |
| R9–R13 | 10 kΩ ¼ W, standing | Same, label rotated | Bus pull-ups on the receiver side | — |
| R1–R8 | 470 Ω ¼ W, standing | Same | Drive-LED series resistors (R1–R4 red, R5–R8 green) | — |
| R19 | 2.2 kΩ ¼ W | Same | +12 V indicator series | — |
| R21 | 470 Ω ¼ W | Same | +5 V indicator series | — |
| D1–D4 | Red 5 mm LED (R) | Circle with a flat; "K" at the flat | Drive 1–4 SELECTED | Flat / short lead = cathode = square pad |
| D5–D8 | Green 5 mm LED (G) | Same | Drive 1–4 WRITE GATE | Same |
| D12, D13 | Yellow 5 mm LED (Y) | Same | "12V" and "5V" present | Same |
| J1 | 34-contact card edge (gold fingers) | Rectangles on the tab; bold numbers = monitored lines 6/10/12/14/24 | Shugart bus | Even pins on top, odd under them; key slot between 4 and 6 |
| J2 | TE/AMP Mate-N-Lok 350211-1 | **Dashed grey**: it sits on the solder side | Power in: 1 +12 V, 2/3 RTN, 4 +5 V | Pin 1 = square pad |
| H1–H4 | M3 mounting holes | Circle in a dashed ring | Standoffs | — |

Conventions: a **square pad** is pin 1, a cathode, or a capacitor's + lead. **Dashed** means a socket or a
part on the solder side. Drive *n* on the board is TRS-80 drive *:n−1*.

## Appendix B — Schematic

![Schematic, as built (r2 BOM), drawn from the netlist in `gen/design.py` (`pdf/schematic.tex`). Gate pin numbers are the DIP-14 pins used in the test steps. KiCad sheet: `output/sa400_led_monitor_schematic.pdf` (A3).](img/schematic.png){width=100%}

## Appendix C — Parts list, as built (JLCPCB r2 BOM)

<span style="color:#0040a0">Values are what JLCPCB fitted. Where the design documents say something else, the design value is in the Notes column.</span>

| Qty | Ref | Part | Value / rating | Package | LCSC | Notes |
|--|---------|------------------------|-----------------|------------------|---------|--------------------------|
| 1 | U1 | TI SN74LS14N hex Schmitt-trigger inverter | — | DIP-14, in socket U1A | C73064 | Bus receivers. Candidate for a 74HCT14 swap (finding F1, step 3.3.7) |
| 1 | U2 | TI SN74LS00N quad 2-input NAND | — | DIP-14, in socket U2A | C181629 | Green LEDs: DSn AND WG |
| 1 | U3 | TI SN74LS06N hex inverter, open collector | — | DIP-14, in socket U3A | C22384767 | Red LEDs: DSn |
| 3 | U1A, U2A, U3A | DIP-14 socket | — | DIP-14 | C190815 | Under U1–U3 |
| 1 | Q1 | IRF4905PBF P-channel MOSFET | 55 V, 74 A, R_DS(on) 20 mΩ at V_GS −10 V | TO-220 vertical, pins G-D-S | C2564 | Reverse-polarity switch. Design called for NDP6020P (logic-level); see step 2.3 |
| 1 | F1 | PTC resettable fuse A72-050 | 0.5 A hold / 1 A trip | radial, 5.08 mm | C135425 | +5 V input |
| 1 | D11 | 1N5339B Zener | 5.6 V, 5 W | DO-15 vertical | C5444832 | Rail clamp; band (cathode) in the square pad |
| 4 | D1–D4 | Kingbright L-53ID red LED | 5 mm, standard brightness | 5 mm | C598429 | SEL 1–4; cathode in the square pad |
| 4 | D5–D8 | Kingbright WP7113GD green LED | 5 mm | 5 mm | C7117617 | WR 1–4 |
| 2 | D12, D13 | Kingbright WP483YDT yellow LED | 5 mm | 5 mm | C6001325 | "12V" and "5V" present |
| 9 | R1–R8, R21 | YAGEO MFR-25JT-52-470R | 470 Ω, ¼ W, 5 % | axial, vertical 7.62 mm | C176518 | LED series, ≈ 5.5–6.5 mA. Design docs: 1.5 kΩ |
| 5 | R14–R18 | YAGEO MFR-25JT-52-470R | 470 Ω, ¼ W, 5 % | axial, vertical 7.62 mm | C176518 | Bus series / fault-current limit |
| 5 | R9–R13 | YAGEO MFR-25JT-52-10K | 10 kΩ, ¼ W, 5 % | axial, vertical 7.62 mm | C176451 | Bus pull-ups (receiver side) |
| 1 | R19 | YAGEO MFR-25FTE52-2K2 | 2.2 kΩ, ¼ W, 1 % | axial, vertical 7.62 mm | C172997 | +12 V indicator series, ≈ 4.5 mA. Design docs: 4.7 kΩ |
| 4 | C1, C2, C3, C6 | Ceramic disc | 100 nF, 50 V | 2.5 mm pitch | C45664 | Decoupling U1–U3; rail entry (C6) |
| 1 | C4 | Electrolytic, radial | 10 µF, 16 V | 5 mm dia, 2.5 mm pitch | C53330112 | Bulk on +5 V; + lead in the square pad |
| 1 | J2 | TE 350211-1 Mate-N-Lok 4-position right-angle header | — | solder side | C305826 | SA400 pinout: 1 +12 V, 2/3 RTN, 4 +5 V; pin 1 = square pad |
| — | J1 | 34-contact card edge, part of the PCB | gold fingers, bevel | — | — | Even pins on the component side, odd (GND) underneath; key slot between 4 and 6 |
| 4 | H1–H4 | M3 × 6 mm standoff + M3 screw (or #4-40) | — | — | — | Not in the JLCPCB order |

Off-board parts for the test run (not on the board). Drawings: Appendix D (jig, pigtail, key plug) and Appendix E (cable).

| Item | Part | Source |
|------------------|------------------------|----------------------------|
| Cable / jig connector | 3M 3463-0001, 34-way card-edge IDC | https://www.mouser.com/c/?q=3463-0001 |
| Power pigtail | TE/AMP 1-480424-0 housing + 60619-1 pins | https://www.te.com/en/product-1-480424-0.html |
| Key plug (pin 4/6 slot) | 3M 3439-2 | https://www.mouser.com/c/?q=3439-2 |
| Jig pull-ups | 150 Ω ¼ W × 5, 5 SPST switches | any |

## Appendix D — Test fixtures (off-board parts for the test run)

![D.1 bus-simulator jig for Phase 2, D.2 power pigtail for J2, D.3 key-plug position. Drawn in `pdf/fixtures.tex`; parts in Appendix C.](img/fixtures.png){width=100%}

## Appendix E — Six-connector cable for Phase 3

![TRS-80 Model I six-connector floppy cable, straight-through, with the DIAG connector second so the terminated drive stays at the far end. `output/cable.png`, built by `gen/build.py`; build notes and the pulled-pin variant in `docs/CABLE.md`.](../output/cable.png){width=100%}
