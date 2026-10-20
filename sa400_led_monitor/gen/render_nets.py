"""Per-net highlight images (GND, +5V) and a copper-only view helper for the document."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import config as C
from design import build, key_slot_x, net_names
from router import Router, F

def routed():
    fps, _ = build(); r = Router(fps, key_slot_x())
    nets = net_names(fps); signal = [n for n in nets if n not in ("GND", "+5V")]
    bus = ["WG_n", "DS3_n", "DS2_n", "DS1_n", "DS4_n"]
    for n in bus + [n for n in signal if n not in bus] + ["+5V", "GND"]:
        r.route_net(n, C.POWER_W if n in ("GND", "+5V") else C.TRACE_W)
    return fps, r

def net_image(fps, r, net, path, caption):
    scale = 8; W, H = int(C.BOARD_W * scale) + 1, int(C.BOARD_H * scale) + 1
    im = Image.new("RGB", (W, H), (30, 60, 40)); d = ImageDraw.Draw(im); S = lambda x, y: (x * scale, y * scale)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception: f = ImageFont.load_default()
    for fp in fps:
        for p in fp.pads:
            hx, hy = p.size[0] / 2 * scale, p.size[1] / 2 * scale; cx, cy = S(p.x, p.y)
            col = (255, 60, 60) if p.net == net else (90, 90, 90)
            (d.rectangle if p.shape == "rect" else d.ellipse)([cx - hx, cy - hy, cx + hx, cy + hy], fill=col)
    for n, l, x1, y1, x2, y2, w in r.segments:
        if n == net:
            d.line([S(x1, y1), S(x2, y2)], fill=(255, 60, 60) if l == F else (255, 160, 60), width=max(2, int(w * scale)))
    for n, x, y in r.via_list:
        if n == net:
            d.ellipse([x * scale - 5, y * scale - 5, x * scale + 5, y * scale + 5], fill=(255, 255, 255))
    d.text(S(3, 46), f"{net} net only: red = F.Cu trace / pad of this net, orange = B.Cu trace, white = via", fill=(255, 255, 255), font=f)
    d.text(S(3, 50), caption, fill=(255, 255, 255), font=f)
    im.save(path)

if __name__ == "__main__":
    fps, r = routed()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    net_image(fps, r, "GND", os.path.join(out, "net_gnd.png"),
              "J2 pin 3 (+5 RTN) -> C4 -> U1.7/13, C1 -> 15 odd fingers of J1 -> U3.7/11/13, C3 -> U2.7, C2.  The B.Cu pour ties all of these too.")
    net_image(fps, r, "+5V", os.path.join(out, "net_5v.png"),
              "J2 pin 4 (+5 V) -> C4 -> U1.14, C1 -> R9..R13 pull-ups -> U2.14, U3.14, C2, C3 -> R1..R8 LED series resistors.")
    print("ok")
