# Six-Connector Floppy Cable — TRS-80 Model I Expansion Interface, 4 drives, 1 diagnostic board

Document: `CABLE.md` · Project: `sa400_led_monitor` · created 2026-09-05, reviewed 2026-09-08 for v0.2.4

---

## 1. Purpose

Radio Shack's four-drive cable for the Model I has five 34-contact card-edge
connectors: one for the Expansion Interface (EI) and one per drive. This cable
adds a sixth for the `sa400_led_monitor` board. Electrically the monitor is a
high-impedance tap (see `THEORY_OF_OPERATION.md` §3.1), so it can sit anywhere
on the ribbon without changing how the drives behave.

---

## 2. Layout

```
   EI          DIAG        DRIVE 0       DRIVE 1       DRIVE 2       DRIVE 3
 [ C1 ]------[ C2 ]-------[ C3 ]--------[ C4 ]--------[ C5 ]--------[ C6 ]
   |   150 mm  |   450 mm    |   200 mm    |   200 mm    |   200 mm    |
 all pins    all pins     :DS1 only    :DS2 only    :DS3 only    :DS4 only   <- if Radio Shack style, see §4
                                                                TERMINATED drive
```

Total length ≈ 1.2 m. Shugart's maximum for the interface is 10 ft (3 m), so
there is room to lengthen any segment; keep the whole thing under 2 m to be safe.

**Why the diagnostic connector goes next to the EI, not at the far end.** The
*last* drive on the cable carries the 150 Ω terminators (Radio Shack 26-1160 /
26-1164 are the terminated drives; 26-1161 is unterminated). Everything past
the terminated drive is an unterminated stub, and a stub of any length is
where reflections live. Putting the monitor second on the cable keeps the
terminated drive at the physical end where it belongs, and gives the monitor a
clean view of every signal the EI drives.

---

## 3. Parts

| Qty | Item | Part | Source |
|---|---|---|---|
| 6 | 34-way card-edge IDC connector, 0.100 in, without mounting flange | **3M 3463-0001** | https://www.mouser.com/c/?q=3463-0001 · datasheet https://multimedia.3m.com/mws/media/22013O/3m-tm-100-in-card-edge-connector-w-o-mounting-flng-ts0010.pdf |
| 1.3 m | 34-conductor flat ribbon cable, 0.050 in pitch, 28 AWG stranded, grey with red #1 stripe | **3M 3365/34** (or 3302/34) | https://www.mouser.com/c/?q=3365%2F34 |
| 6 (optional) | Strain relief for 3463 | 3M 3448-56 | https://www.mouser.com/c/?q=3448-56 |
| 1 (optional) | Key plug for the diagnostic board's slot | 3M 3439-2 | https://www.mouser.com/c/?q=3439-2 |

All six connectors are the same part; the EI's disk connector is a 34-contact
card edge exactly like a drive's. The monitor board's tab is built to the same
3M drawing as the drives, so it takes the same connector too.

Substitutes: the AMP 583717-1 / 583717-5 and the Panduit 34-way "card edge
IDC" are equivalents if 3M stock is thin.

---

## 4. Drive select — two ways to wire it, pick one

The Model I's controller puts DRIVE SELECT 1–4 on pins 10, 12, 14 and 6. Which
drive answers to which line was handled two different ways over the years, and
the cable has to match the drives:

### 4a. Straight-through (recommended)

Every connector has all 34 contacts. Each drive is set to its own select line
with the DIP switch / shunt on the drive (your SA400's S1–S3 block does this:
one position on, the others off). Drive 0 = DS1 = pin 10, drive 1 = DS2 =
pin 12, drive 2 = DS3 = pin 14, drive 3 = DS4 = pin 6.

Simplest to build, nothing to remove, any connector fits any position, and
the cable works with any Shugart-compatible drive.

### 4b. Radio Shack "pulled pin" style

Radio Shack shipped Model I drives with **all four** select positions enabled
on the shunt and made the cable decide: on each drive connector three of the
four select contacts are removed, so a drive only ever sees the one line for
its position.

| Connector | Keep contact | Remove contacts |
|---|---|---|
| C3 drive 0 | 10 | 12, 14, 6 |
| C4 drive 1 | 12 | 10, 14, 6 |
| C5 drive 2 | 14 | 10, 12, 6 |
| C6 drive 3 | 6 | 10, 12, 14 |
| C1 EI, C2 DIAG | all | none |

Use this only if your drives are still shunted for all four selects. If a
drive with all selects enabled goes on a straight cable, it answers to every
drive number and two drives fight on the data lines — the symptom is the
system "selecting both drives" that the SVD notes describe.

**Removing a contact from a 3M 3463.** The U-contacts are held in the body by
the cover. Before pressing the cover, grip the unwanted contact at the
insulation-displacement end with fine pliers and pull it straight out of the
body; the ribbon conductor above it stays intact so the line still reaches
the drives further along. Mark the connector (label maker on the strain
relief) with the drive number — a mis-positioned pulled-pin connector is a
miserable fault to find later.

The diagnostic board's connector **must** keep all contacts in either scheme:
it needs all four select lines and WRITE GATE.

---

## 5. Pin 1 and orientation

* Ribbon conductor 1 (red stripe) goes to contact 1 of every connector.
  Contact 1 is the odd row on one face of the 3M connector and is marked with
  a triangle on the body.
* On every card edge — EI, drives, monitor — pin 1 is on the **solder side**
  and pin 2 directly above it on the **component side**. Viewed from the
  component side with the fingers pointing away from you, pin 2 is at the
  right. The key slot between pins 4 and 6 is therefore near that end.
* All six connectors go on the ribbon the same way up. Because the cable is
  straight-through, orientation is the only thing that can go wrong: a
  connector on backwards puts grounds on all the signal lines (odd pins are
  all ground), which is harmless but the drive will not respond.

---

## 6. Assembly

1. Cut the ribbon to length and square the ends. Mark the connector positions
   with tape at 150 / 450 / 200 / 200 / 200 mm from the EI end.
2. For each position, lay the ribbon into the connector body with the red
   stripe on the contact-1 side (triangle). Check the stripe is on the same
   side at every position before pressing anything.
3. If using scheme 4b, pull the unwanted contacts now (§4b).
4. Press the cover on. The 3M 3640 press with the 3443-63 locator is the
   proper tool; a bench vise with two flat wooden blocks works for one-off
   cables — press evenly until the cover clips lock, do not rock it.
5. Fit strain reliefs if used.
6. Buzz every conductor end to end with a meter: 34 conductors, no adjacent
   shorts, and (for 4b) confirm the pulled contacts read open at that
   connector only.

---

## 7. Check before first use

* Terminated drive is at the far end (C6). Every other drive has its
  terminator removed.
* Only one drive is set to each select (4a), or each drive connector keeps
  exactly one select contact (4b).
* Red stripe on the same edge at all six connectors.
* Monitor board is powered from its own J2 (standard drive power plug: +5 V runs it, +12 V lights the "12V" indicator); the ribbon carries no power.

Power the system with only the EI and the monitor connected first. With no
drives, the monitor's red LEDs should follow the select lines as the ROM
tries to boot from drive 0 (RED 1 flashes, then the "DISKETTE?" prompt); no
green should ever light without a write.

---

## 8. Model I quirks worth knowing

* Model I drives are single-sided; pin 32 (SIDE SELECT) is unused by the
  stock EI. Double-sided modifications re-purpose it, and some conflict with
  DS4 on pin 6 — with such a mod only three drives can be used.
* Early EIs were sensitive to interference on this cable; Radio Shack later
  supplied a shielded ribbon. If the machine boots unreliably with the
  longer cable, shorten the EI-to-drive-0 run first.
* The EI's disk connector is on its front-left underside; leave enough slack
  from C1 to C2 that the monitor board can sit on the desk beside the EI.
