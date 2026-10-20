# Reply to JLCPCB — order SMT0261xxxxxxx (order no. kept off GitHub)

Document: `JLCPCB_REPLY_EMAIL.md` · 2026-10-07 · board rev v0.2.3 (silkscreen-only change from v0.2.2)

## What happened

JLCPCB's engineer rendered the v0.2.2 board and asked two things: (1) are the THT parts oriented
correctly, (2) where do U1/U2/U3 go. The render was **electrically correct**; the only reason they
asked is that our v0.2.2 silkscreen drew the Q1 (TO-220) body box on the wrong side of the pin row, so
their 3D body did not sit in our box. v0.2.3 fixes the silkscreen (body outline, "TAB" band toward the
J2 edge, G/D/S under the pads). Copper, solder mask, drills and outline are unchanged — verified by
rendering every v0.2.2 and v0.2.3 gerber layer with gerbv and diffing them pixel by pixel.

## How to send it (3 steps)

1. **Reply to their email** (keep the subject line — it carries the order number, that is how it reaches
   the engineer who asked). Do not open a new ticket.
2. **Attach two files**, nothing else:
   - `sa400_led_monitor_v0.2.3_gerbers_JLCPCB.zip` (131 kB, 12 files — the replacement gerber)
   - `jlcpcb_orientation_reply.png` (their render with every part marked up)
   **Do not attach** the BOM/CPL again (the ones on the order already carry the LCSC numbers and the
   U1A/U2A/U3A socket rows — the v0.2.3 generator output is the same list) and do not attach the project zip.
3. **Paste the text below** as the body. It answers both questions, asks them to swap the gerber, and
   tells them to proceed with the current file if a swap is not possible — so there is no second round trip.

If the order page offers "Replace file" / re-upload for the PCB, you can also upload the zip there, but
the email is enough — the engineer can swap it.

## Reply text (copy from the line below to the end)

---

Subject: Re: [your order SMT0261xxxxxxx (order no. kept off GitHub)] — orientation confirmed + silkscreen-only gerber update

Hello,

Thank you for checking. Answers for order SMT0261xxxxxxx (order no. kept off GitHub):

1) Orientation of THT parts on your 3D render: ALL CORRECT — please build exactly as rendered.
   - Q1 (IRF4905PBF, TO-220): correct as rendered. Metal tab toward the board edge with J2 (top of
     the render), plastic label face toward the board centre. Pin 1 = GATE = square pad (left),
     pin 2 = DRAIN, pin 3 = SOURCE. The silkscreen rectangle drawn below the three pads in the file
     you have is a drawing error on our side — please ignore it.
   - D11 (1N5339B): cathode band at the square (upper) pad — correct. Horizontal mounting is fine.
   - C4 (10 uF electrolytic): + lead in the square (upper) pad, stripe toward the lower pad — correct.
   - D1–D8, D12, D13 (5 mm LEDs): cathode (flat side, short lead) in the square pad = LEFT pad of
     every LED, as the flat line on the silkscreen shows — correct.
   - F1, C1, C2, C3, C6, R1–R21: non-polarized, any orientation.
   - J2 (Mate-N-Lok 350211-1): BOTTOM side. Pin 1 (+12 V) = square pad = the pad nearest the board
     centre (next to Q1); pin 4 (+5 V) nearest corner hole H1. Housing latch opening faces the
     recessed rear edge (the J1 card-edge side). Please confirm on your bottom-side render.

2) Where to place U1, U2, U3: they are the ICs for the three DIP-14 sockets U1A, U2A, U3A.
   Solder the sockets at the U1/U2/U3 positions (same coordinates in the CPL), then plug U1 into
   U1A, U2 into U2A, U3 into U3A. Notch at the LEFT end as the silkscreen shows (pin 1 = square
   pad, bottom-left). The IC sits centred in the socket — the ~1 mm offset of the IC body in your
   3D view is only a model offset.

3) Replacement gerber (optional, silkscreen only): attached is sa400_led_monitor_v0.2.3_gerbers_JLCPCB.zip.
   The ONLY change is the silkscreen — the Q1 body outline is now drawn correctly (with "TAB" and
   G/D/S markings) and the revision text reads v0.2.3. Copper, solder mask, drill files and board
   outline are identical to the file on the order. Please replace the gerber with this zip if that
   is possible at this stage. If it is not, please proceed with the current file — everything above
   applies to it unchanged, and the BOM/CPL on the order stay as they are.

The attached PNG is your render with each part's orientation marked.

Thank you,
Ven

---

## If they answer with another question

- "Which side is the tab?" — toward the J2 / rear edge (the edge with the card-edge fingers and the
  power header). On the v0.2.3 silkscreen it is the band marked TAB.
- "Can we use a different TO-220 part?" — only a P-channel MOSFET with pin order G-D-S (IRF4905,
  NDP6020P, IRF9540 all qualify).
- "LED colour per position?" — D1–D4 red, D5–D8 green, D12–D13 yellow (BOM is already matched).
- Anything else about files: send only the gerber zip; never the project zip.
