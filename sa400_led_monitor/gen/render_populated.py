"""
render_populated.py — wireframe top view of the POPULATED sa400_led_monitor board.

Every part body (ICs in sockets, LEDs, resistors, capacitors, Q1, D11, F1, and J2 as a dashed
ghost because it sits on the solder side) is drawn as an outline at its real footprint position
from gen/design.py. Labels show the AS-BUILT values (JLCPCB r2 BOM). Black on white, made for print.

Usage (from the project root):
    python gen/render_populated.py                  -> output/board_populated.png + .pdf
    python gen/render_populated.py --out docs/img   -> same files into another folder

Exit codes: 0 ok, 1 error, 130 interrupted (Ctrl-C).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# As-built values (JLCPCB r2 BOM). The design source still carries the design-time values.
AS_BUILT = {**{f"R{n}": "470" for n in range(1, 9)}, "R21": "470", "R19": "2k2",
            **{f"R{n}": "10k" for n in range(9, 14)}, **{f"R{n}": "470" for n in range(14, 19)},
            "Q1": "IRF4905"}

INK = "black"
LW = 0.7          # body outline
LW_THIN = 0.45    # pads, leads, details
GHOST = "#777777"  # solder-side part


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "output"))
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Arc
    import config as C
    import design

    fps, _ = design.build()
    by = {f.ref: f for f in fps}

    fig = plt.figure(figsize=(C.BOARD_W / 18, (C.BOARD_H + 4) / 18))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-2, C.BOARD_W + 2)
    ax.set_ylim(C.BOARD_H + 2, -3)
    ax.set_aspect("equal")
    ax.axis("off")

    def box(x, y, w, h, r=0.0, lw=LW, ec=INK, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    fc="none", ec=ec, lw=lw, ls=ls))

    def circ(x, y, r, lw=LW, ec=INK, ls="-"):
        ax.add_patch(Circle((x, y), r, fc="none", ec=ec, lw=lw, ls=ls))

    def line(xs, ys, lw=LW_THIN, ec=INK, ls="-"):
        ax.plot(xs, ys, color=ec, lw=lw, ls=ls, solid_capstyle="round")

    def txt(x, y, s, size=5.2, bold=False, color=INK, **kw):
        ax.text(x, y, s, fontsize=size, color=color, ha=kw.pop("ha", "center"), va=kw.pop("va", "center"),
                fontfamily="DejaVu Sans", fontweight="bold" if bold else "normal", **kw)

    # ---- board outline: recessed rear edge, tab, key slot
    tl, tr, rec = design.tab_left(), C.J1_TAB_RIGHT, C.J1_REAR_RECESS
    ks = design.key_slot_x() if C.J1_KEY_SLOT else None
    kw2 = C.J1_KEY_SLOT_W / 2
    outline = [(0, rec), (tl, rec), (tl, 0)]
    if ks is not None:
        outline += [(ks - kw2, 0), (ks - kw2, C.J1_KEY_SLOT_DEPTH), (ks + kw2, C.J1_KEY_SLOT_DEPTH), (ks + kw2, 0)]
    outline += [(tr, 0), (tr, rec), (C.BOARD_W, rec), (C.BOARD_W, C.BOARD_H), (0, C.BOARD_H), (0, rec)]
    line([p[0] for p in outline], [p[1] for p in outline], lw=1.3)

    # ---- J1 fingers (component side = even pins)
    x2 = C.J1_TAB_RIGHT - C.J1_PIN2_FROM_RIGHT_EDGE
    for p in by["J1"].pads:
        if p.drill:
            circ(p.x, p.y, p.drill / 2, lw=LW_THIN)
        elif p.layers[0].startswith("F"):
            ax.add_patch(Rectangle((p.x - p.size[0] / 2, p.y - p.size[1] / 2), p.size[0], p.size[1],
                                   fc="none", ec=INK, lw=LW_THIN))
    for pin in range(2, 35, 2):
        x = x2 - (pin - 2) / 2 * C.J1_PITCH
        mon = pin in (6, 10, 12, 14, 24)
        txt(x, C.J1_FINGER_DEPTH + 1.9, str(pin), 3.6 if not mon else 4.2, bold=mon)
    txt((tl + tr) / 2, -1.8, "J1 — 34-pin Shugart bus card edge (bold numbers = monitored lines)", 5.0)

    # ---- every other through-hole pad (small circle), mounting holes
    for f in fps:
        if f.ref in ("J1", "J2"):
            continue
        for p in f.pads:
            if f.ref.startswith("H"):
                circ(p.x, p.y, C.MOUNT_HOLE_DRILL / 2, lw=LW)
                circ(p.x, p.y, C.MOUNT_HOLE_PAD / 2, lw=LW_THIN, ls=(0, (2, 1.5)))
                continue
            if p.shape == "rect":
                s = min(p.size) * 0.55
                ax.add_patch(Rectangle((p.x - s / 2, p.y - s / 2), s, s, fc="none", ec=INK, lw=LW_THIN))
            else:
                circ(p.x, p.y, min(p.size) * 0.28, lw=LW_THIN)

    # ---- J2 on the solder side: dashed ghost
    j2 = sorted(by["J2"].pads, key=lambda q: int(q.number))
    xs = [p.x for p in j2]
    box(min(xs) - 4, rec + 0.6, max(xs) - min(xs) + 8, C.J2_ROW_Y + 4 - rec - 0.6, ec=GHOST, ls=(0, (3, 2)))
    for i, p in enumerate(j2):
        if i == 0:
            ax.add_patch(Rectangle((p.x - 1.2, p.y - 1.2), 2.4, 2.4, fc="none", ec=GHOST, lw=LW_THIN))
        else:
            circ(p.x, p.y, 1.2, lw=LW_THIN, ec=GHOST)
        txt(p.x, p.y - 3.2, f"{p.number}", 4.0, color=GHOST)
        txt(p.x, p.y + 2.9, ["+12V", "RTN", "RTN", "+5V"][i], 3.8, color=GHOST)
    txt((min(xs) + max(xs)) / 2, C.J2_ROW_Y + 6.2, "J2 power — on SOLDER side (dashed)", 4.6, color=GHOST)

    # ---- part bodies
    for f in fps:
        ref, val = f.ref, AS_BUILT.get(f.ref, f.value)
        lib = f.lib_name.split(":")[1]
        pads = {p.number: p for p in f.pads}

        if lib.startswith("DIP-14"):
            p1, p14 = pads["1"], pads["14"]
            x0, x1 = p1.x - 1.9, pads["7"].x + 1.9
            box(x0 - 0.5, p14.y - 1.5, x1 - x0 + 1.0, p1.y - p14.y + 3.0, lw=LW_THIN, ls=(0, (2, 1.2)))  # socket
            box(x0, p14.y + 0.7, x1 - x0, p1.y - p14.y - 1.4, r=0.4)                                        # IC
            ax.add_patch(Arc((x0, (p1.y + p14.y) / 2), 2.2, 2.2, theta1=-90, theta2=90, ec=INK, lw=LW))     # notch
            circ(p1.x + 0.3, p1.y - 2.1, 0.4, lw=LW_THIN)                                                    # pin-1 dot
            txt((x0 + x1) / 2, (p1.y + p14.y) / 2 - 0.9, val, 6.0, bold=True)
            txt((x0 + x1) / 2, (p1.y + p14.y) / 2 + 1.3, ref, 5.0)

        elif lib.startswith("R_Axial"):
            p1, p2 = pads["1"], pads["2"]
            line([p1.x, p2.x], [p1.y + 1.35, p2.y])
            circ(p1.x, p1.y, 1.35)
            if ref in ("R9", "R10", "R11", "R12", "R13"):
                txt(p1.x - 1.9, (p1.y + p2.y) / 2 + 0.6, f"{ref} {val}", 4.2, rotation=90)
            else:
                txt(p1.x, p1.y - 2.5, ref, 4.6, bold=True)
                txt(p2.x, p2.y + 2.1, val, 4.0)

        elif lib.startswith("LED"):
            k, a = pads["1"], pads["2"]
            cx, cy = (k.x + a.x) / 2, k.y
            ax.add_patch(Arc((cx, cy), 5.8, 5.8, theta1=-62, theta2=242, ec=INK, lw=LW))   # rim, open on flat
            fx = cx - 2.9 * 0.47
            line([fx, fx], [cy - 2.56, cy + 2.56], lw=LW)                                    # flat = cathode (K)
            circ(cx, cy, 2.5, lw=LW_THIN)
            colour = {"RED": "R", "GREEN": "G", "YELLOW": "Y"}[f.value]
            txt(cx, cy - 4.1, ref, 4.6, bold=True)
            txt(cx, cy + 4.0, colour, 4.2)
            txt(fx - 0.9, cy + 2.6, "K", 3.2)

        elif lib.startswith("C_Disc"):
            p1, p2 = pads["1"], pads["2"]
            box(p1.x - 1.2, p1.y - 1.3, 2.4, p2.y - p1.y + 2.6, r=1.1)
            if ref == "C6":
                txt(p1.x, p2.y + 2.6, ref, 4.6, bold=True)
            else:
                txt(p1.x + 2.6, (p1.y + p2.y) / 2, ref, 4.6, bold=True, ha="left")

        elif lib.startswith("CP_Radial"):
            p1, p2 = pads["1"], pads["2"]
            cy = (p1.y + p2.y) / 2
            circ(p1.x, cy, 2.5)
            line([p1.x - 1.7, p1.x + 1.7], [cy + 1.8, cy + 1.8], lw=LW_THIN)   # minus-stripe side
            txt(p1.x + 2.2, p1.y - 1.9, "+", 6.0, bold=True)
            txt(p1.x, cy - 3.8, ref, 4.6, bold=True)
            txt(p1.x, cy + 3.7, "10µ", 4.0)

        elif lib.startswith("TO-220"):
            pa, pc = pads["1"], pads["3"]
            box(pa.x - 2.6, pa.y + 0.9, pc.x - pa.x + 5.2, 3.6)                       # body
            box(pa.x - 2.6, pa.y + 4.5, pc.x - pa.x + 5.2, 1.3, lw=LW_THIN)           # metal tab
            for p, n in ((pa, "G"), (pads["2"], "D"), (pc, "S")):
                txt(p.x, p.y - 2.4, n, 3.8)
            txt((pa.x + pc.x) / 2, pa.y + 2.7, val, 4.0)
            txt((pa.x + pc.x) / 2, pa.y + 7.5, ref, 4.6, bold=True)

        elif lib.startswith("D_DO-15"):
            k, a = pads["1"], pads["2"]
            line([k.x, a.x], [k.y + 1.8, a.y])
            circ(k.x, k.y, 1.8)
            circ(k.x, k.y, 1.25, lw=LW_THIN)        # band ring = cathode end up
            txt(k.x, k.y - 3.0, ref, 4.6, bold=True)
            txt(a.x + 2.0, a.y, "5V6", 4.0, ha="left")

        elif lib.startswith("Fuse"):
            p1, p2 = pads["1"], pads["2"]
            box(p1.x - 1.4, p1.y - 1.6, p2.x - p1.x + 2.8, 3.2, r=1.4)
            txt((p1.x + p2.x) / 2, p1.y - 3.0, ref, 4.6, bold=True)
            txt((p1.x + p2.x) / 2, p1.y + 3.0, "PTC 0.5A", 4.0)

        elif ref.startswith("H"):
            txt(f.x, f.y - 4.4, ref, 4.6, bold=True)

    # ---- titles and drive labels
    txt(48, 52, "sa400_led_monitor v0.2.2 — populated, as built (r2 BOM)", 7.2, bold=True)
    txt(48, 56.5, "Component side, top view · J1 fingers point away · J1 pin 2 at right", 5.2)
    txt(48, 60.5, "Dashed = socket or solder-side part · square pad = pin 1 / cathode / +", 5.2)
    for n, x in enumerate([34.29, 59.69, 85.09, 110.49]):
        txt(x, 124.2, f"DRIVE {n + 1}  (TRS-80 :{n})", 5.4, bold=True)

    os.makedirs(args.out, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(args.out, f"board_populated.{ext}"), dpi=300, facecolor="white")
    print(f"[render_populated] wrote {args.out}/board_populated.png and .pdf")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[render_populated] interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[render_populated] FAILED: {e}", file=sys.stderr)
        sys.exit(1)
