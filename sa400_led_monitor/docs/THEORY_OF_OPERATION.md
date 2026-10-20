# Theory of Operation — SA400 Form-Factor Drive-Select / Write-Gate LED Monitor

Document: `THEORY_OF_OPERATION.md` · Project: `sa400_led_monitor` · Version 0.2.4 · created 2026-09-05, updated 2026-10-19 (design-review corrections in §3.0, §4.2, §4.3, marked in red; J2 on the component side)

---

## 1. What the board does

The board plugs onto the 34-conductor Shugart floppy bus as if it were a fifth
drive and shows, on eight LEDs, which of the four possible drives the host is
currently addressing and whether the host is writing to it:

| LED | Colour | Lights when |
|---|---|---|
| D1–D4 "SEL" | red | the host asserts DRIVE SELECT 1–4 |
| D5–D8 "WR" | green | the host asserts DRIVE SELECT *n* **and** WRITE GATE |

It is powered from a standard 4-pin drive power plug exactly as an SA400 is (+5 V
for the logic, +12 V present), adds no termination and negligible load to the
bus, never drives the bus, and is built so that no single failure on the board
can put damaging current into the host's bus drivers (section 4).

Two yellow LEDs beside the power header show that +12 V and +5 V are present.

---

## 2. The Shugart bus, from first principles

### 2.1 Physical layer

The interface defined in the SA400L OEM manual (Shugart P/N 39019-1, section
3) is a 34-conductor ribbon cable. On the drive it lands on a card-edge
connector, J1, whose 34 contacts are arranged as 17 pairs: the even-numbered
contacts (2–34) on the component side of the board, the odd-numbered (1–33)
directly under them on the solder side. **Every odd contact is ground.** The
signals are therefore interleaved with grounds along the ribbon, which keeps
crosstalk down on a cable that may run several feet.

The five contacts this board uses:

| J1 pin | Signal | Direction (host ↔ drive) |
|---|---|---|
| 10 | DRIVE SELECT 1 | host → drive |
| 12 | DRIVE SELECT 2 | host → drive |
| 14 | DRIVE SELECT 3 | host → drive |
| 6  | DRIVE SELECT 4 | host → drive |
| 24 | WRITE GATE | host → drive |

All other even contacts (INDEX, STEP, DIRECTION, MOTOR ON, WRITE DATA, READ
DATA, TRACK 00, WRITE PROTECT, and the spares 2, 4, 32, 34) are present as
fingers so the connector seats normally, but have **no copper path** onto the
board. The board cannot affect them.

### 2.2 Electrical layer: open-collector, active-low

Every signal on this bus is *active-low* and driven by an *open-collector*
gate. Both facts are central to how the board works, so they deserve a proper
explanation.

**Open-collector.** The manual specifies a 7438 as the host's driver. A 7438
output has only a transistor to ground — no transistor to +5 V. When the gate
wants to assert the line it turns that transistor on and *pulls the line down*
to about 0.4 V. When it wants to release the line it simply turns the
transistor off, and the line floats. Something else must pull the line up to
+5 V when nobody is pulling it down; on this bus that "something" is the
terminator.

**Terminator.** The *last* drive on the cable carries a 150 Ω pull-up resistor
pack from each signal line to +5 V (SA400L manual section 3.2.1). 150 Ω is
low enough that the line rises quickly through the cable's capacitance, and
it sets the current the host driver must sink when it asserts a line:
(5 V − 0.4 V) / 150 Ω ≈ 31 mA. A 7438 is rated to sink 48 mA, so one
terminator is fine and two would be marginal. **This is why the board must not
carry its own terminators**: a second 150 Ω pack in parallel would halve the
resistance and push the host driver past its rating.

**Active-low.** Because the only strong action a driver can take is to pull
down, "asserted" is defined as the low state:

| Line voltage | Meaning |
|---|---|
| ≈ 0.4 V (pulled down by the host) | signal **asserted** (DRIVE SELECT n active, WRITE GATE active) |
| ≈ 5 V (pulled up by the terminator) | signal **released** |

In the schematic these bus-side nets carry the suffix `_n` (DS1_n … DS4_n,
WG_n) to mark them active-low.

**Receiver.** The manual recommends a 7414 as the receiver in each drive. A
7414 is a hex Schmitt-trigger inverter. Two properties matter:

1. *It inverts.* A low (asserted) input gives a high output, so after the
   receiver the logic becomes active-high, which is easier to think about.
2. *It has hysteresis.* A plain TTL input switches at one threshold, around
   1.3 V, so a slowly rising or noisy line can make it chatter. A Schmitt
   input has two thresholds — it switches high at about 1.7 V and low at
   about 0.9 V — and the 0.8 V gap between them swallows ringing and ground
   bounce on a long ribbon. This is exactly why Shugart specifies it.

### 2.3 Timing: what "selected" and "writing" look like

The host asserts one DRIVE SELECT line for as long as it is talking to that
drive: at minimum a few hundred microseconds for a single step command, more
typically tens to hundreds of milliseconds for a read or write. WRITE GATE is
asserted only while write current is actually flowing to the head, and only
while a DRIVE SELECT is also asserted (the manual requires DRIVE SELECT to be
active at least 100 µs before WRITE GATE).

The LEDs follow the lines directly, with no stretching. That is a deliberate
choice for v0.1: what you see is the truth. A very short access can produce a
flash too brief to notice; if that matters in practice, a pulse-stretcher is
listed in `TODO.md` as a v0.2 option.

---

## 3. Signal path on the board

```
                              +5V
                               |
                              10k  (R9-R13, one per line)
                               |
 J1 pin ---- 470R (R14-R18) ---+---->|>o---- DSn / WG  (active-HIGH from here on)
 (active-low)  DSn_n    DSn_in    U1 74LS14
                                  Schmitt inverter
```

Net names: `DSn_n` / `WG_n` is the finger side (active-low, bus), `DSn_in` /
`WG_in` is the node after the series resistor, `DSn` / `WG` is the inverted,
active-high output of U1.

### 3.0 Series resistors — R14–R18, 470 Ω

Each monitored finger reaches the rest of the board only through a 470 Ω
resistor. Nothing else on the board — not the pull-up, not the receiver —
touches the finger directly. Electrically the resistor costs 0.19 V (the LS14's
0.4 mA input current through 470 Ω), so a bus low of 0.4 V arrives at the
receiver as 0.59 V, still well under the Schmitt trigger's 0.9 V lower
threshold. What it buys is a bound on the current the board can ever push into
the host: worked through in section 4.2.

<span style="color:#b00000">**Correction, 2026-10-19 design review.** The 0.59 V above counts only the receiver's input current.
R9–R13 sit on the *receiver* side of R14–R18, so when the bus is low their ≈ 0.44 mA also leaves through
the series resistor: worst case 0.4 V + (0.4 mA I_IL + 0.44 mA) × 470 Ω ≈ **0.79 V** at the LS14 input,
against SN74LS14 V_T− = 0.5 V min / 0.8 V typ / 1.0 V max. Typical parts (V_OL ≈ 0.25 V, I_IL ≈ 0.2 mA)
give ≈ 0.55 V, so the board works on *typical* margin, not worst-case margin. It is measured on the real
bus in `TEST_PLAN.md` step 3.3.7. Remedies: a 74HCT14 in U1 removes the I_IL term with no board change
(its input current is µA); moving the pull-ups to the finger side of the series resistor removes the
pull-up term (planned for v0.3, see `V0.3_PLAN.md`). With both, the receiver sees the bus voltage itself.</span>

### 3.1 Receiver stage — U1, 74LS14

Each of the five bus lines goes from its series resistor to one input of U1.
The output is the inverted, cleaned-up signal: **DSn is high when drive n is
selected; WG is high when the host is writing.**

*Loading.* A 74LS14 input sources at most 0.4 mA when the line is held low
(IIL). Compared with the 31 mA the terminator already makes the host driver
sink, that is 1.3 % — the host will not notice. This is what "high-impedance
tap" means here: the board is invisible to the bus.

*Pull-ups.* R9–R13 are 10 kΩ from each receiver node (`DSn_in`) to +5 V. On a
properly terminated bus they do almost nothing (10 kΩ in parallel with 150 Ω
is still 148 Ω). Their job is to define the inputs when the board is powered
but the cable is unplugged, or plugged into a cable whose last drive has had
its terminator pulled: without them the LS14 inputs would float and the LEDs
could flicker at random. 10 kΩ (plus the 470 Ω) adds only 0.5 mA to what the
host sinks.

*Spare gate.* Gate 6 of U1 is unused. Its input (pin 13) is tied to ground so
it sits in a defined state; its output (pin 12) is left open. Floating TTL
inputs tend to read high but can oscillate and add supply noise, so tying
them off is standard practice.

### 3.2 Red — U3, 74LS06 open-collector inverter

```
        +5V ---- 470R ---- RED LED ---- U3 output (open collector)
                        (anode)    (cathode)
```

RED n must light whenever DSn is high, regardless of WRITE GATE. That is just
an inverter feeding a low-side LED: when DSn goes high the 74LS06 output pulls
its cathode to ground and the LED conducts through the 470 Ω resistor from
+5 V. When DSn is low the output transistor is off, the cathode floats up to
+5 V through the LED, no current flows, LED off.

Why a 74LS06 rather than the spare gate on U1 or another 74LS14? Two reasons:

* Sink capability. A 74LS06 output is rated to sink 40 mA; a 74LS14 only
  8 mA. At the ≈ 5.5 mA we run the LEDs either would do, but the 74LS06 leaves
  headroom for brighter LEDs later without any other change.
* Open collector. With no pull-up transistor inside, the output can be pulled
  up to any voltage the LED chain needs; there is nothing fighting it.

### 3.3 Green — U2, 74LS00 quad NAND

```
      DSn ----\
               NAND ---- GREEN LED cathode
      WG  ----/            (anode via 470R to +5V)
```

GREEN n must light only when drive n is selected **and** WRITE GATE is active.
A NAND gate gives a low output exactly when both inputs are high — which is
precisely the condition, since both DSn and WG are active-high after U1. The
low output sinks the green LED the same way the 74LS06 sinks the red one.

The truth table for one drive:

| DSn | WG | RED (U3 out) | GREEN (U2 out) | What you see |
|---|---|---|---|---|
| 0 | x | high (off) | high (off) | nothing — drive not selected |
| 1 | 0 | **low (on)** | high (off) | red — selected, reading/seeking |
| 1 | 1 | **low (on)** | **low (on)** | red **and** green — writing |

Per your spec, red stays on during a write; green joins it. A 74LS00 output
sinks 8 mA (V_OL ≤ 0.5 V); the ≈ 5.5 mA of a standard LED through 470 Ω stays
inside that, and the 1.5 kΩ high-efficiency option (≈ 1.8 mA) is far inside it.

### 3.4 LED current

The LED chain is +5 V → R → LED → gate output. The board is built with the
standard-brightness 5 mm LEDs JLCPCB stocks (Kingbright L-53ID red, WP7113GD
green, WP483YDT yellow), which want 5–10 mA, so R1–R8 and R21 are **470 Ω**.
With the output saturated at about 0.4 V and a red LED dropping ≈ 1.9 V:

    I = (5.0 − 0.4 − 1.9) / 470 Ω ≈ 5.7 mA

Green parts drop ≈ 2.1 V, giving ≈ 5.3 mA; both are inside the 74LS00's 8 mA
sink. If you fit high-efficiency LEDs (Kingbright WP7113LID / WP7113LGD, bright
at 2 mA) use 1.5 kΩ instead (≈ 1.8 mA). Total worst-case LED current with all
eight lit (impossible in practice — only one drive is selected at a time) is
≈ 45 mA; the normal case, one red + one green, is ≈ 11 mA.

---

## 4. Power and protection

J2 carries the SA400 pinout, and the board uses the two rails exactly as the drive does: **+5 V for the
logic**, **+12 V present** on the other pair. (The SA400 spends its +12 V on motors; this board has none,
so +12 V lights an indicator and nothing else.)

```
J2-4 +5V  ─ F1 PTC 0.5 A ─ Q1 P-MOSFET (D→S, gate to GND) ─┬─ +5V ─┬─ to the logic, LEDs, pull-ups
                                                            │       │
                                                    D11 1N5339B   C6 100n, C4 10u        R21 470R → D13 "5V"
                                                    5.6 V clamp
J2-1 +12V ─ R19 2k2 ─ D12 "12V" ─ GND
J2-2 +12 RTN ─┐
J2-3 +5  RTN ─┴─ GND (also the 15 odd fingers of J1)
```

| Part | Job | Why this value |
|---|---|---|
| F1 PTC 0.5 A hold / 1 A trip | Limits energy into any downstream fault; resets when the fault clears | Board draws ≈ 45 mA |
| Q1 IRF4905PBF P-channel MOSFET (TO-220, pins G-D-S), drain in / source out / gate to GND | Reverse-polarity switch: with +5 V the correct way round the body diode conducts, then V_GS = −5 V turns the channel on (**a few millivolts drop** at 45 mA); reversed, the body diode is blocked and V_GS is positive, so nothing conducts | A series diode would drop 0.35–0.7 V, below the 74LS minimum V_CC of 4.75 V. IRF4905 is what JLCPCB stocks (V_GS(th) −2…−4 V, 20 mΩ at −10 V — only partly enhanced at −5 V, which at 45 mA does not matter); the logic-level onsemi NDP6020P (50 mΩ at −4.5 V) is the drop-in alternative. Mount with the metal tab toward the J2 edge: pin 1 (gate) is the square pad |
| D11 1N5339B 5.6 V 5 W Zener, +5 V to GND | Clamps the rail if the wrong voltage arrives (e.g. +12 V on the +5 V pin): holds ≈ 6 V and pulls current until F1 trips | 74LS absolute maximum V_CC is 7 V |
| C6 100 nF, C4 10 µF | Rail decoupling at the entry point | — |
| R19 2.2 kΩ + D12 yellow | "+12 V present" indicator, ≈ 4.5 mA | Confirms the cable is a real drive cable with both rails |
| R21 470 Ω + D13 yellow | "+5 V rail up" indicator, ≈ 6 mA | Shows the PTC hasn't tripped |
| R14–R18 470 Ω series in each bus line | Limits any current the board could push into the bus | See §4.2 |

### 4.0 J2 — the power connector

J2 is a 4-position Commercial Mate-N-Lok header, the family the SA400 uses, with the
drive's pinout. The SA400 carries it on the solder side; this board carried it there too
up to 0.2.3, and JLCPCB's single-sided (Economic) assembly left it unpopulated. From 0.2.4
it is a **right-angle header on the component side** (TE 1-641737-1; the vertical 350211-1
fits the same pads), with the mating face at the recessed rear edge so the drive power plug
still enters from the rear, beside the ribbon.

| Pin | Signal | Used for |
|---|---|---|
| 1 | +12 V | "12V" indicator D12 through R19 (≈ 4.5 mA); nothing else |
| 2 | +12 V return | GND |
| 3 | +5 V return | GND |
| 4 | +5 V | logic supply, through F1 and Q1 |

Pin 1 is the square pad, at the H1 (corner) end of the row; `1 +12V 2 RTN 3 RTN 4 +5V`
and "J2 PWR IN – SA400 pinout" are printed just below the housing so they
stay readable with the header fitted.

*Handedness.* A keyed plug guarantees that plug pin 1 meets header pin 1 — it does **not**
guarantee which end of the footprint header pin 1 lands on; that depends on the header's
own construction, and moving the header from the solder side to the component side mirrors
it (what was at the board-centre end viewed from the top is now at the corner end). The
0.2.0–0.2.3 layout (pin 1 at the centre end, solder side) and the 0.2.4 layout (pin 1 at the
corner end, component side) are the same assumption seen from the two sides. It is checked
on the bench, not on paper: header in its holes, drive plug on, continuity from the plug's
yellow (+12 V) wire to the pad marked +12V. If it lands on +5V instead, the header belongs
on the other side of the board (or `J2_PIN1_X`/`J2_PIN_DIR` flip and the board is rebuilt).
The protection chain (F1, D11) is sized to survive a +12 V-on-+5 V mistake, but it should
never be relied on for that.

### 4.1 Current budget (+5 V)

| Consumer | Typical |
|---|---|
| U1 74LS14 | 10 mA |
| U2 74LS00 | 4 mA |
| U3 74LS06 | 10 mA |
| Drive LEDs (two lit, 470 Ω) | 11 mA |
| Pull-ups (5 lines held low) | 2.5 mA |
| D13 indicator | 6 mA |
| **Total on +5 V** | **≈ 45 mA** (≈ 80 mA if all eight drive LEDs were lit) |
| +12 V (D12 indicator) | 4.5 mA |

### 4.2 Why the series resistors protect the Expansion Interface

The Shugart bus is driven from the EI by 7438 open-collector gates whose outputs are rated for 5.5 V and
48 mA sink. The 470 Ω resistors sit between each finger and everything else on the board (pull-up and
receiver), so:

- A failed receiver shorting a bus line to the board's rail can push at most (5.6 − 0.4) / 470 ≈ 11 mA
  into the EI's driver — the rail cannot exceed 5.6 V because of D11. Added to the terminator's 31 mA
  that is 42 mA, inside the 7438's 48 mA rating.
- Hot-plug transients on the card edge see 470 Ω before the LS14 input.
- The receiver still works: 0.4 mA of LS14 input current through 470 Ω drops 0.19 V, so a line at 0.4 V
  reaches the input at 0.59 V — under the Schmitt trigger's 0.9 V lower threshold.
  <span style="color:#b00000">Corrected 2026-10-19: with the pull-up current included the worst case is ≈ 0.79 V against a 0.5 V
  minimum threshold — see §3.0. The fault-current bound in the first bullet is unaffected.</span>

### 4.3 Fault table

| Fault | What happens | Effect on the EI |
|---|---|---|
| +12 V and +5 V swapped in a miswired cable | D11 clamps the rail at ≈ 6 V. <span style="color:#b00000">Corrected 2026-10-19: the current is *not* ≈ 1 A — a cold 0.5 A PTC is ≈ 0.5 Ω, so until F1 trips it is whatever the supply, cable and Q1 will pass (amps). F1 trips well inside a second at that level; D11 may fail, normally short, which leaves the board dead but the rail at 0 V.</span> D12 dark, D13 dim | Bus sees ≤ 11 mA per line until F1 trips (§4.2); a shorted D11 afterwards means 0 mA |
| Reversed +5 V | Q1 stays off; nothing conducts | None |
| Reversed +12 V | Only R19/D12 see it. <span style="color:#b00000">Corrected 2026-10-19: D12 does not simply block — a 5 mm LED is rated ≈ 5 V reverse, so it is driven ≈ 7 V into reverse breakdown at ≈ 3 mA through R19. It will most likely survive; v0.3 adds a 1N4148 in series.</span> | None |
| Spike on +5 V | D11 absorbs (5 W); F1 limits | None |
| LS14 input shorted to rail | 470 Ω limits to ≈ 11 mA | Within the 7438 rating |
| Board unpowered, EI on | ≈ 0.6 mA per line into the dead inputs through 470 Ω + 10 kΩ | 0.1 V on a 150 Ω-terminated line |
| Board powered, EI off | ≈ 0.5 mA per line into the EI through 10 kΩ + 470 Ω | Harmless |

Ground is common to both PSU returns (J2 pins 2 and 3) and to the bus (fifteen odd fingers), exactly as
in a drive; the receivers judge the bus lines against that ground.

## 5. Why 74LS and not 74HCT

74HCT would draw less current and load the bus even less (input current in
microamps). It was not chosen because:

* The whole point of the board is to look like a 1979 Shugart drive; 74LS
  DIPs are in period.
* 74HCT outputs are rated for only 4 mA per pin (25 mA absolute maximum).
  The 74LS06's 40 mA sink is far more comfortable for LEDs.
* 74LS14 is the modern equivalent of the 7414 Shugart specifies; its
  thresholds and hysteresis are designed for exactly this bus.

Substituting 74HCT14 / 74HCT00 / 74HCT06 (all pin-compatible) would work if
the LED resistors were raised to keep each output under 4 mA. This is noted
in `TODO.md`.

---

## 6. What the board deliberately does not do

* **Does not terminate** the bus (section 2.2).
* **Does not drive** anything onto the bus — no output pin of any IC touches
  J1.
* **Does not draw** from +12 V beyond a 4.5 mA indicator.
* **Does not connect** any finger directly to a semiconductor — every monitored
  line passes through 470 Ω first (section 3.0).
* **Does not stretch** LED pulses (section 2.3).

---

## 7. References

1. Shugart SA400L Minifloppy OEM Manual, P/N 39019-1, Nov 1982 — interface
   pinout §3.2, electrical §3.2.1, J2 pinout §3.3, card edge fig 3-2.
   https://www.bitsavers.org/pdf/shugart/SA400/39019-1_SA400L_OEM_Manual_Nov82.pdf
2. Shugart SA400 Service Manual, P/N 54096-2, Apr 1979 — schematics and parts
   catalogue (PCB clamps 54036).
   https://archive.org/details/bitsavers_shugartSA4eApr79_4138915
3. 3M Card-Edge .100 in Connector, TS-0010-14 — recommended PCB layout for
   the 3463 (34-way) connector.
   https://multimedia.3m.com/mws/media/22013O/3m-tm-100-in-card-edge-connector-w-o-mounting-flng-ts0010.pdf
4. TEAC FD-55 Specification — fig 103, card-edge dimensions (cross-check).
   https://deramp.com/downloads/floppy_drives/teac/TEAC%20FD-55GFR.pdf
5. TI SN74LS14, SN74LS00, SN74LS06 datasheets — https://www.ti.com/product/SN74LS14 ,
   https://www.ti.com/product/SN74LS00 , https://www.ti.com/product/SN74LS06
