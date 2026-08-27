"""The Soulforge — renders the Soulkeep sigil (an ethereal soulstone holding a
captured soul-wisp, bound by gold keeper's claws) at any size.

Run directly to regenerate icon-512.png / icon-192.png / icon.ico;
app.py imports draw_sigil() for the brag card.

Craft law learned the hard way: Pillow's GaussianBlur on RGBA drags the
transparent pixels' BLACK rgb into every soft edge. Every glow layer must be
created color-filled at alpha 0 ("_layer") so blur only feathers the alpha.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

# Midnight palette
STONE_DARK = (26, 18, 58)
VIOLET = (177, 92, 255)
GLOW = (199, 125, 255)
TEAL = (111, 224, 192)
TEAL_HI = (208, 250, 233)
GOLD = (243, 199, 102)
INK = (237, 233, 255)


def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _layer(S, color):
    """A blur-safe layer: color everywhere, alpha zero."""
    return Image.new("RGBA", (S, S), tuple(color) + (0,))


def _soft(img, layer, blur):
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_sigil(size, pad_frac=0.0):
    """Return an RGBA Image of the sigil. Renders 4x supersampled."""
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S / 2
    R = S * (0.5 - pad_frac) * 0.68  # stone radius

    # -- ambient halo ------------------------------------------------------
    halo = _layer(S, GLOW)
    hd = ImageDraw.Draw(halo)
    hd.ellipse((cx - R * 1.22, cy - R * 1.22, cx + R * 1.22, cy + R * 1.22), fill=GLOW + (66,))
    _soft(img, halo, S * 0.035)

    # -- stone: facets softened into one crystal body ----------------------
    stone = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd0 = ImageDraw.Draw(stone)
    sd0.ellipse((cx - R, cy - R, cx + R, cy + R), fill=STONE_DARK + (255,))
    for i in range(8):
        a0 = -112.5 + i * 45
        mid = math.radians(a0 + 22.5)
        lit = (math.cos(mid - math.radians(-135)) + 1) / 2  # 1 facing up-left
        base = (
            int(50 + 58 * lit),
            int(31 + 40 * lit),
            int(110 + 106 * lit),
        )
        sd0.pieslice((cx - R, cy - R, cx + R, cy + R), start=a0, end=a0 + 45,
                     fill=base + (255,))
    stone = stone.filter(ImageFilter.GaussianBlur(S * 0.006))
    img.alpha_composite(stone)

    # inner-depth vignette: the glass darkens as it curves away
    vig = _layer(S, (14, 9, 34))
    vd = ImageDraw.Draw(vig)
    vd.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(14, 9, 34, 150),
               width=int(R * 0.22))
    _soft(img, vig, S * 0.020)

    # luminous core rising from the gem's depths
    core = _layer(S, (116, 74, 208))
    cd = ImageDraw.Draw(core)
    cd.ellipse((cx - R * 0.56, cy - R * 0.56, cx + R * 0.56, cy + R * 0.56),
               fill=(116, 74, 208, 190))
    _soft(img, core, S * 0.035)
    core2 = _layer(S, (158, 112, 244))
    cd2 = ImageDraw.Draw(core2)
    cd2.ellipse((cx - R * 0.34, cy - R * 0.34, cx + R * 0.34, cy + R * 0.34),
                fill=(158, 112, 244, 190))
    _soft(img, core2, S * 0.035)

    # -- nebula mist drifting inside the glass -----------------------------
    for col, blobs in (
        ((120, 70, 220), ((0.52, 205, 0.30, 70), (0.70, 330, 0.22, 55))),
        ((64, 42, 140), ((0.55, 55, 0.34, 80), (0.66, 130, 0.20, 60))),
        ((111, 224, 192), ((0.46, 250, 0.16, 34),)),
    ):
        mist = _layer(S, col)
        md = ImageDraw.Draw(mist)
        for rr, ang, rad, al in blobs:
            x, y = _pt(cx, cy, R * rr, ang)
            e = R * rad
            md.ellipse((x - e * 1.5, y - e, x + e * 1.5, y + e), fill=tuple(col) + (al,))
        _soft(img, mist, S * 0.030)

    # -- soul-dust: faint motes adrift in the stone ------------------------
    dust = _layer(S, INK)
    dd = ImageDraw.Draw(dust)
    motes = ((0.74, 12, 0.012, 200), (0.62, 48, 0.008, 150), (0.80, 66, 0.010, 170),
             (0.55, 96, 0.007, 130), (0.72, 118, 0.011, 180), (0.85, 38, 0.006, 110),
             (0.40, 150, 0.006, 120), (0.66, 258, 0.007, 120), (0.82, 292, 0.009, 140),
             (0.30, 320, 0.005, 100), (0.58, 180, 0.006, 110), (0.88, 12, 0.005, 90),
             (0.60, 315, 0.008, 150), (0.76, 338, 0.006, 120))
    for sr, sa, sz2, al in motes:
        x, y = _pt(cx, cy, R * sr, sa)
        rr2 = S * sz2 / 2
        dd.ellipse((x - rr2, y - rr2, x + rr2, y + rr2), fill=INK + (al,))
    _soft(img, dust, S * 0.0035)
    # the three brightest motes keep a sharper heart
    d = ImageDraw.Draw(img)
    for sr, sa, sz2, al in motes[:3]:
        x, y = _pt(cx, cy, R * sr, sa)
        rr2 = S * sz2 / 3.2
        d.ellipse((x - rr2, y - rr2, x + rr2, y + rr2), fill=INK + (min(255, al + 40),))

    # -- the kept soul: three vapor strands spiraling to a blooming heart --
    hx, hy = cx - R * 0.10, cy - R * 0.08
    strands = ((1.00, 0, 1.00), (1.07, 14, 0.42), (0.92, -16, 0.36))
    soul = _layer(S, TEAL)
    sd = ImageDraw.Draw(soul)
    steps = 90
    for mul, off, amp in strands:
        for i in range(steps):
            t = i / (steps - 1)
            ang = -30 + off + t * 268
            rr = R * (0.14 + 0.41 * t) * mul
            w = ((1 - t) ** 1.6 * R * 0.115 + R * 0.008) * (0.55 + 0.45 * amp)
            x, y = _pt(hx, hy, rr, ang)
            a = int(235 * (1 - t) ** 0.68 * amp + 8)
            sd.ellipse((x - w, y - w, x + w, y + w), fill=TEAL + (a,))
    _soft(img, soul, S * 0.016)          # vapor pass
    _soft(img, soul, S * 0.005)          # body pass

    # heart: a bloom, not a bead — layered radiance with no hard edge
    for col, rad, al, bl in ((TEAL, 0.30, 120, 0.020), (TEAL, 0.19, 170, 0.011),
                             (TEAL_HI, 0.115, 220, 0.007), ((245, 255, 250), 0.055, 255, 0.004)):
        beat = _layer(S, col)
        bd = ImageDraw.Draw(beat)
        e = R * rad
        bd.ellipse((hx - e, hy - e, hx + e, hy + e), fill=tuple(col) + (al,))
        _soft(img, beat, S * bl)

    # -- rim: a soft ring of light with a thin bright edge -----------------
    rimglow = _layer(S, VIOLET)
    rg = ImageDraw.Draw(rimglow)
    rg.ellipse((cx - R, cy - R, cx + R, cy + R), outline=VIOLET + (200,),
               width=max(4, int(S * 0.010)))
    _soft(img, rimglow, S * 0.008)
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(210, 170, 255, 150),
              width=max(2, S // 400))
    # breath of light on the upper-left rim
    lc = _layer(S, INK)
    ld = ImageDraw.Draw(lc)
    ld.arc((cx - R, cy - R, cx + R, cy + R), start=175, end=250,
           fill=INK + (210,), width=max(3, S // 260))
    _soft(img, lc, S * 0.006)

    # -- gold keeper's claws, with a soft candle-bloom ---------------------
    Rc = R * 1.17
    cw = max(4, int(S * 0.019))
    box = (cx - Rc, cy - Rc, cx + Rc, cy + Rc)
    gl = _layer(S, GOLD)
    gd = ImageDraw.Draw(gl)
    gd.arc(box, start=-58, end=32, fill=GOLD + (255,), width=cw)
    gd.arc(box, start=122, end=212, fill=GOLD + (255,), width=cw)
    for tip in (-58, 32, 122, 212):
        x0, y0 = _pt(cx, cy, Rc, tip)
        x1, y1 = _pt(cx, cy, R * 1.035, tip)
        gd.line([(x0, y0), (x1, y1)], fill=GOLD + (255,), width=cw)
    _soft(img, gl, S * 0.010)            # bloom
    _soft(img, gl, S * 0.0022)           # metal

    # -- spark where the light kisses the claw -----------------------------
    spark = _layer(S, INK)
    spd = ImageDraw.Draw(spark)
    sx, sy = _pt(cx, cy, Rc, 208)
    sl = S * 0.034
    for ang, ll in ((0, sl), (90, sl), (45, sl * 0.4), (135, sl * 0.4)):
        x0, y0 = _pt(sx, sy, ll, ang)
        x1, y1 = _pt(sx, sy, ll, ang + 180)
        spd.line([(x0, y0), (x1, y1)], fill=INK + (230,), width=max(2, S // 300))
    _soft(img, spark, S * 0.003)
    d.ellipse((sx - S * 0.005, sy - S * 0.005, sx + S * 0.005, sy + S * 0.005),
              fill=(255, 255, 255, 255))

    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    big = draw_sigil(512)
    big.save(os.path.join(here, "icon-512.png"))
    draw_sigil(192).save(os.path.join(here, "icon-192.png"))
    big.save(os.path.join(here, "icon.ico"),
             sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("sigil forged: icon-512.png, icon-192.png, icon.ico")
