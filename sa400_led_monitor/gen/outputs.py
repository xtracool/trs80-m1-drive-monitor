#!/usr/bin/env python3
"""Review outputs that are not part of the fab set: KiCad raytraced renders, copper views, schematic
PDF, STEP model, placement and net images, J2 label crop.  Run after gen/verify.py has passed.

    python3 gen/outputs.py --kicad-bin DIR      # DIR holds kicad-cli (KiCad 10)

Writes into output/: render_top.png, render_bottom.png, copper_top.png, copper_bottom.png,
board_top_kicad.png, sa400_led_monitor_schematic.pdf, sa400_led_monitor.step, placement.png,
net_gnd.png, net_5v.png, net_5v_in.png, j2_labels.png.  (j1_vs_photo.png and j1_root_holes.png are
photo comparisons made once for v0.1.x and kept.)

Exit 0 on success, 1 on a failed step, 130 on Ctrl-C.
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, "kicad"); O = os.path.join(ROOT, "output")
PCB = os.path.join(K, "sa400_led_monitor.kicad_pcb"); SCH = os.path.join(K, "sa400_led_monitor.kicad_sch")


def run(cmd, env, timeout=600):
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
        raise RuntimeError("failed: " + " ".join(cmd[:4]))


def main():
    kbin = None
    if "--kicad-bin" in sys.argv:
        kbin = sys.argv[sys.argv.index("--kicad-bin") + 1]
    cli = os.path.join(kbin, "kicad-cli") if kbin else "kicad-cli"
    env = dict(os.environ)
    if kbin:
        env["APPDIR"] = os.path.dirname(kbin)
    os.makedirs(O, exist_ok=True)

    print("[1/6] raytraced renders (top, bottom)")
    for side in ("top", "bottom"):
        run([cli, "pcb", "render", "--output", os.path.join(O, f"render_{side}.png"), "--side", side,
             "--width", "1800", "--height", "1700", "--quality", "high", "--background", "opaque", PCB], env)

    print("[2/6] copper views (SVG -> PNG)")
    import cairosvg
    views = {"copper_top": ("F.Cu,F.SilkS,Edge.Cuts", []),
             "copper_bottom": ("B.Cu,B.SilkS,Edge.Cuts", ["--mirror"]),
             "board_top": ("F.Cu,F.Mask,F.SilkS,Edge.Cuts", [])}
    for name, (layers, extra) in views.items():
        svg = os.path.join(O, name + ".svg")
        run([cli, "pcb", "export", "svg", "--output", svg, "--layers", layers, "--page-size-mode", "2",
             "--exclude-drawing-sheet"] + extra + [PCB], env)
        png = os.path.join(O, ("board_top_kicad" if name == "board_top" else name) + ".png")
        cairosvg.svg2png(url=svg, write_to=png, output_width=1800, background_color="white")
        os.remove(svg)

    print("[3/6] schematic PDF, STEP")
    run([cli, "sch", "export", "pdf", "--output", os.path.join(O, "sa400_led_monitor_schematic.pdf"), SCH], env)
    run([cli, "pcb", "export", "step", "--output", os.path.join(O, "sa400_led_monitor.step"), "--subst-models", PCB], env)

    print("[4/6] placement and net images")
    run([sys.executable, os.path.join(ROOT, "gen", "render_placement.py"), os.path.join(O, "placement.png")], env)
    run([sys.executable, os.path.join(ROOT, "gen", "render_nets.py")], env)

    print("[5/6] J2 label crop (component side)")
    from PIL import Image
    im = Image.open(os.path.join(O, "render_top.png"))
    w, h = im.size
    im.crop((0, 0, int(w * 0.36), int(h * 0.26))).save(os.path.join(O, "j2_labels.png"))

    print("[6/6] done")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[outputs] interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:                      # crash -> exit 1, distinct from Ctrl-C
        print(f"[outputs] FAILED: {e}", file=sys.stderr)
        sys.exit(1)
