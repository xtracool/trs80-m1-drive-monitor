"""Quick PNG preview of the board (independent of KiCad) for design review."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import config as C
from design import build, key_slot_x
from router import Router, F, B

def render(r, fps, path, scale=8):
    W, H = int(C.BOARD_W*scale)+1, int(C.BOARD_H*scale)+1
    im = Image.new("RGB", (W, H), (20, 60, 30))
    d = ImageDraw.Draw(im)
    S = lambda x, y: (x*scale, y*scale)
    # traces B first then F
    for layer, col in ((B, (60, 100, 220)), (F, (220, 60, 60))):
        for net, l, x1, y1, x2, y2, w in r.segments:
            if l != layer: continue
            d.line([S(x1,y1), S(x2,y2)], fill=col, width=max(1,int(w*scale)))
    for net, x, y in r.via_list:
        rr = C.VIA_DIA/2*scale
        d.ellipse([x*scale-rr, y*scale-rr, x*scale+rr, y*scale+rr], fill=(200,200,200))
    for fp in fps:
        for p in fp.pads:
            hx, hy = p.size[0]/2*scale, p.size[1]/2*scale
            col = (240, 200, 60) if any(l.startswith(("F","*")) for l in p.layers) else (120,120,200)
            box = [p.x*scale-hx, p.y*scale-hy, p.x*scale+hx, p.y*scale+hy]
            (d.rectangle if p.shape=="rect" else d.ellipse)(box, fill=col)
            if p.drill:
                rr = p.drill/2*scale
                d.ellipse([p.x*scale-rr, p.y*scale-rr, p.x*scale+rr, p.y*scale+rr], fill=(0,0,0))
        for item in fp.silk:
            if item[0]=="line": d.line([S(item[1],item[2]), S(item[3],item[4])], fill=(255,255,255), width=1)
            elif item[0]=="rect": d.rectangle([S(item[1],item[2]), S(item[3],item[4])], outline=(255,255,255))
            elif item[0]=="circle": 
                cx,cy,rr = item[1]*scale, item[2]*scale, item[3]*scale
                d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr], outline=(255,255,255))
        d.text(S(fp.x-2, fp.y-5), fp.ref, fill=(255,255,255))
    ks = key_slot_x()
    d.rectangle([S(ks-C.J1_KEY_SLOT_W/2, 0), S(ks+C.J1_KEY_SLOT_W/2, C.J1_KEY_SLOT_DEPTH)], fill=(0,0,0))
    d.rectangle([0,0,W-1,H-1], outline=(255,255,0))
    im.save(path)

if __name__ == "__main__":
    fps, _ = build()
    r = Router(fps, key_slot_x())
    import build as bld
    # replicate routing order
    from design import net_names
    nets = net_names(fps)
    signal = [n for n in nets if n not in ("GND","+5V")]
    bus = ["WG_n","DS3_n","DS2_n","DS1_n","DS4_n"]
    for n in bus + [n for n in signal if n not in bus] + ["+5V","GND"]:
        r.route_net(n, C.POWER_W if n in ("GND","+5V") else C.TRACE_W)
    render(r, fps, sys.argv[1] if len(sys.argv)>1 else "/home/claude/sa400_led_monitor/output/preview.png")
