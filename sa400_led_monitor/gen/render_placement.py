"""Placement-only preview (no routing): component outlines, pads, refs, key dimensions."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
import config as C
from design import build, key_slot_x, tab_left

def main(path):
    fps, _ = build()
    scale = 9
    M = 60  # margin for dimension text
    W, H = int(C.BOARD_W*scale)+2*M, int(C.BOARD_H*scale)+2*M
    im = Image.new("RGB", (W, H), (245, 245, 245))
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        fontb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        fonts = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except Exception:
        font = fontb = fonts = ImageFont.load_default()
    S = lambda x, y: (M + x*scale, M + y*scale)
    # board
    d.rectangle([S(0,0), S(C.BOARD_W, C.BOARD_H)], fill=(30, 90, 50), outline=(255, 220, 0), width=3)
    ks = key_slot_x(); tl = tab_left(); R = C.J1_REAR_RECESS
    d.rectangle([S(-0.5, -0.5), S(tl, R)], fill=(245,245,245))
    d.rectangle([S(C.J1_TAB_RIGHT, -0.5), S(C.BOARD_W+0.5, R)], fill=(245,245,245))
    d.line([S(0, R), S(tl, R), S(tl, 0), S(C.J1_TAB_RIGHT, 0), S(C.J1_TAB_RIGHT, R), S(C.BOARD_W, R)], fill=(255,220,0), width=3)
    if C.J1_KEY_SLOT:
        d.rectangle([S(ks-C.J1_KEY_SLOT_W/2, 0), S(ks+C.J1_KEY_SLOT_W/2, C.J1_KEY_SLOT_DEPTH)], fill=(245,245,245))
    for fp in fps:
        top = fp.layer == "F.Cu"
        if fp.courtyard:
            x1,y1,x2,y2 = fp.courtyard
            d.rectangle([S(x1,y1), S(x2,y2)], outline=(200,200,200) if top else (255,120,255), width=1)
        for item in fp.silk:
            col = (255,255,255) if top else (255,120,255)
            if item[0]=="line": d.line([S(item[1],item[2]), S(item[3],item[4])], fill=col, width=2)
            elif item[0]=="rect": d.rectangle([S(item[1],item[2]), S(item[3],item[4])], outline=col, width=2)
            elif item[0]=="circle":
                cx,cy = S(item[1],item[2]); rr=item[3]*scale
                d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr], outline=col, width=2)
        for p in sorted(fp.pads, key=lambda q: any(l.startswith(("F","*")) for l in q.layers)):
            hx, hy = p.size[0]/2*scale, p.size[1]/2*scale
            onF = any(l.startswith(("F","*")) for l in p.layers)
            col = (240,200,60) if onF else (150,150,230)
            cx, cy = S(p.x, p.y)
            box = [cx-hx, cy-hy, cx+hx, cy+hy]
            if fp.ref == "J1" and not onF:
                d.rectangle([cx-hx+2, cy-hy, cx+hx-2, cy+hy+6*scale*0], outline=col, width=1)
                d.text((cx-6, cy+hy+16), p.number, fill=(150,150,230), font=fonts)
                continue
            (d.rectangle if p.shape=="rect" else d.ellipse)(box, fill=col)
            if fp.ref == "J1":
                d.text((cx-6, cy+hy+3), p.number, fill=(255,255,255), font=fonts)
            if p.drill:
                rr = p.drill/2*scale
                d.ellipse([cx-rr,cy-rr,cx+rr,cy+rr], fill=(0,0,0))
        # reference label
        if fp.ref == "J1":
            d.text(S(tl-4, 17.5), "J1  34-pin card edge on a 45.59 mm tab.  white = even pins (top), blue = odd/GND (bottom)", fill=(255,255,255), font=fonts)
            d.text(S(tl-42, R+1.0), "rear edge recessed 11.43 mm both sides of the tab (photo)", fill=(255,220,0), font=fonts)
        else:
            lx, ly = (fp.courtyard[0], fp.courtyard[1]-1.6) if fp.courtyard else (fp.x, fp.y)
            d.text(S(lx, ly), f"{fp.ref} {fp.value}" if fp.ref[0] in "UJC" else fp.ref,
                   fill=(255,255,255) if top else (255,120,255), font=font)
    # annotations
    d.text(S(4, 47), "COMPONENT SIDE (top view).  All parts on this side since 0.2.4 (J2 was on the solder side before).", fill=(255,255,255), font=fontb)
    d.text(S(4, 51), "Rear edge = y 0 (top of picture): J1 fingers point away, J2 Mate-N-Lok at the other corner.",
           fill=(255,255,255), font=font)
    d.text(S(4, 54.5), "Front edge (bottom): LED pairs per drive - SEL (red) / WR (green).", fill=(255,255,255), font=font)
    d.text(S(4, 58), "Signal flow: J1 -> R9..R13 pull-ups -> U1 74LS14 -> U2 74LS00 / U3 74LS06 -> LEDs",
           fill=(255,255,255), font=font)
    for n in range(4):
        x = 30.48 + 25.4*n
        d.text(S(x-4, 110), f"DRIVE {n+1}", fill=(255,255,255), font=fontb)
        d.text(S(x-3.2, 122), "SEL", fill=(255,80,80), font=fonts); d.text(S(x+2.6, 122), "WR", fill=(80,255,80), font=fonts)
    # dimensions
    d.line([S(0, -3), S(C.BOARD_W, -3)], fill=(0,0,0), width=1)
    d.text((M + C.BOARD_W*scale/2 - 60, M - 40), f"{C.BOARD_W:.2f} mm  (5.500 in)", fill=(0,0,0), font=fontb)
    d.line([S(-3, 0), S(-3, C.BOARD_H)], fill=(0,0,0), width=1)
    d.text((5, M + C.BOARD_H*scale/2), f"{C.BOARD_H:.1f}\n(5.0 in)", fill=(0,0,0), font=font)
    x2 = C.J1_TAB_RIGHT - C.J1_PIN2_FROM_RIGHT_EDGE
    d.text(S(x2-46, -6.5), f"tab {tl:.2f}..{C.J1_TAB_RIGHT:.1f}  pin 34 @ {x2-16*2.54:.2f}  pin 2 @ {x2:.2f}  key slot: {'cut' if C.J1_KEY_SLOT else 'none (photo)'}", fill=(0,0,0), font=fonts)
    d.text(S(2, -6.5), f"J2 pins y={C.J2_ROW_Y} (component side, right-angle, mating face at the recess) pin1 x={C.J2_PIN1_X} (H1 end), pin4 x={C.J2_PIN1_X + 3*C.J2_PIN_DIR*C.J2_PITCH:.2f}", fill=(0,0,0), font=fonts)
    for i,(x,y) in enumerate(C.MOUNT_HOLES):
        d.text(S(x-3, y+3.5), f"H{i+1} ({x:.2f},{y:.2f})", fill=(255,255,255), font=fonts)
    im.save(path)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "placement.png"))
