"""The Soulforge — renders the Soulkeep sigil: a glass sphere lit from within
by the spiral soul it keeps, its far side dissolving into the deep, a broken
trail of gold embers where the keeper's binding once burned.

Run directly to regenerate icon-512.png / icon-192.png / icon.ico;
app.py imports draw_sigil() for the brag card.

Craft laws learned at this forge:
- Pillow's GaussianBlur on RGBA drags the transparent pixels' BLACK rgb into
  every soft edge; every glow layer must be color-filled at alpha 0 (_layer).
- Symmetry is sticker-language: one light source (the soul), asymmetric rim,
  turbulence instead of gradients, nothing perfectly closed.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

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


def _soft(dst, layer, blur):
    dst.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_sigil(size, pad_frac=0.0):
    """Return an RGBA Image of the sigil. Renders 4x supersampled."""
    rnd = random.Random(1404)
    S = size * 4
    cx = cy = S / 2
    R = S * (0.5 - pad_frac) * 0.70          # sphere radius
    hx, hy = cx - R * 0.16, cy - R * 0.14    # the soul: the only light source

    # ======================= the interior, built unclipped ================
    interior = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(interior)
    # deep glass, almost night
    bd.ellipse((cx - R * 1.02, cy - R * 1.02, cx + R * 1.02, cy + R * 1.02),
               fill=(13, 10, 32, 255))
    # light of the soul filling the glass, dying toward the far side
    for col, rad, al, bl in (((58, 38, 128), 1.02, 235, 0.10),
                             ((96, 60, 190), 0.72, 210, 0.07),
                             ((130, 86, 226), 0.44, 190, 0.045)):
        lay = _layer(S, col)
        ld = ImageDraw.Draw(lay)
        e = R * rad
        ld.ellipse((hx - e, hy - e, hx + e, hy + e), fill=tuple(col) + (al,))
        _soft(interior, lay, S * bl)

    # -- turbulence: three octaves of smoke, colors drifting ---------------
    octaves = (
        (R * 0.34, S * 0.045, 16, ((40, 26, 96), (74, 46, 156))),
        (R * 0.18, S * 0.022, 26, ((96, 60, 190), (58, 36, 128), (128, 62, 176))),
        (R * 0.09, S * 0.010, 30, ((120, 80, 214), (86, 100, 190))),
    )
    for rad, blur, n, cols in octaves:
        for col in cols:
            lay = _layer(S, col)
            ld = ImageDraw.Draw(lay)
            for _ in range(n // len(cols)):
                ang = rnd.uniform(0, 360)
                rr = R * (0.15 + 0.80 * math.sqrt(rnd.random()))
                x, y = _pt(cx, cy, rr, ang)
                dist = math.hypot(x - hx, y - hy) / (2 * R)
                al = int((22 + 34 * rnd.random()) * (1.0 - 0.55 * dist))
                w = rad * rnd.uniform(0.55, 1.5)
                h = w * rnd.uniform(0.45, 0.9)
                th = rnd.uniform(0, 1)
                # smear each puff along its own drift line
                for k in range(3):
                    ox = (k - 1) * w * 0.5 * math.cos(th * 6.28)
                    oy = (k - 1) * w * 0.5 * math.sin(th * 6.28)
                    ld.ellipse((x + ox - w, y + oy - h, x + ox + w, y + oy + h),
                               fill=tuple(col) + (al,))
            _soft(interior, lay, blur)

    # -- the soul: a two-armed spiral of living vapor ----------------------
    vapor = _layer(S, TEAL)
    vd = ImageDraw.Draw(vapor)
    body = _layer(S, TEAL)
    bd2 = ImageDraw.Draw(body)
    for arm_off, arm_amp in ((0, 1.0), (180, 0.72)):
        for i in range(110):
            t = i / 109
            theta = t * 300                                    # degrees of wind
            rr = R * 0.055 * math.exp(0.0075 * theta)          # log spiral
            if rr > R * 0.66:
                break
            ang = -35 + arm_off + theta
            x, y = _pt(hx, hy, rr, ang)
            jx = rnd.uniform(-1, 1) * R * 0.012 * t
            jy = rnd.uniform(-1, 1) * R * 0.012 * t
            w = (1 - t) ** 1.25 * R * 0.075 * arm_amp + R * 0.006
            a = int(245 * (1 - t) ** 0.8 * arm_amp + 6)
            vd.ellipse((x + jx - w * 1.9, y + jy - w * 1.9, x + jx + w * 1.9, y + jy + w * 1.9),
                       fill=TEAL + (int(a * 0.35),))
            bd2.ellipse((x + jx - w, y + jy - w, x + jx + w, y + jy + w),
                        fill=TEAL + (a,))
    _soft(interior, vapor, S * 0.020)
    _soft(interior, body, S * 0.0045)
    # nucleus: layered radiance, hot white heart
    for col, rad, al, bl in ((TEAL, 0.26, 130, 0.020), (TEAL, 0.15, 185, 0.010),
                             (TEAL_HI, 0.085, 235, 0.006), ((250, 255, 252), 0.038, 255, 0.0032)):
        lay = _layer(S, col)
        ld = ImageDraw.Draw(lay)
        e = R * rad
        ld.ellipse((hx - e, hy - e, hx + e, hy + e), fill=tuple(col) + (al,))
        _soft(interior, lay, S * bl)

    # -- motes: sparse, some in focus, some bokeh --------------------------
    for col, picks in ((INK, 9), (TEAL_HI, 4)):
        lay = _layer(S, col)
        ld = ImageDraw.Draw(lay)
        crisp = []
        for _ in range(picks):
            ang = rnd.uniform(0, 360)
            rr = R * (0.30 + 0.62 * rnd.random())
            x, y = _pt(cx, cy, rr, ang)
            dist = math.hypot(x - hx, y - hy) / (2 * R)
            r0 = S * rnd.uniform(0.0018, 0.0060)
            al = int((90 + 130 * rnd.random()) * (1.0 - 0.45 * dist))
            ld.ellipse((x - r0, y - r0, x + r0, y + r0), fill=tuple(col) + (al,))
            if rnd.random() < 0.5:
                crisp.append((x, y, r0 * 0.5, min(255, al + 60)))
        _soft(interior, lay, S * 0.004)
        idd = ImageDraw.Draw(interior)
        for x, y, r0, al in crisp:
            idd.ellipse((x - r0, y - r0, x + r0, y + r0), fill=tuple(col) + (al,))

    # -- sphere shading: light dies with distance from the soul ------------
    shade = _layer(S, (6, 4, 16))
    sd = ImageDraw.Draw(shade)
    for k in range(9):
        f = k / 8
        rr = R * (0.85 + 1.35 * f)
        al = int(10 + 165 * f ** 1.6)
        sd.ellipse((hx - rr, hy - rr, hx + rr, hy + rr),
                   outline=(6, 4, 16, al), width=int(R * 0.19))
    _soft(interior, shade, S * 0.024)

    # ======================= clip to the glass ============================
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(S * 0.0015))
    interior.putalpha(Image.composite(interior.split()[3], Image.new("L", (S, S), 0), mask))

    # ======================= assembly =====================================
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # light spilling out of the glass, strongest where the soul burns
    spill = _layer(S, GLOW)
    spd = ImageDraw.Draw(spill)
    e = R * 1.10
    spd.ellipse((hx - e, hy - e, hx + e, hy + e), fill=GLOW + (58,))
    _soft(img, spill, S * 0.030)
    img.alpha_composite(interior)

    d = ImageDraw.Draw(img)
    # rim: lit only where the soul reaches it — stepped arcs, never a badge ring
    rim = _layer(S, (222, 186, 255))
    rd = ImageDraw.Draw(rim)
    soul_ang = math.degrees(math.atan2(hy - cy, hx - cx))      # ~ -139°
    for k in range(26):
        f = k / 25
        seg = 148 * (1 - f * 0.92)
        al = int(16 + 225 * (1 - f) ** 2.2)
        a0 = soul_ang - seg / 2
        rd.arc((cx - R, cy - R, cx + R, cy + R), start=a0, end=a0 + seg,
               fill=(222, 186, 255, al), width=max(2, int(S * 0.0035)))
    _soft(img, rim, S * 0.0035)
    # a whisper of fresnel on the dark side, so the glass reads as glass
    fr = _layer(S, (120, 100, 190))
    fd = ImageDraw.Draw(fr)
    fd.arc((cx - R * 0.995, cy - R * 0.995, cx + R * 0.995, cy + R * 0.995),
           start=soul_ang + 150, end=soul_ang + 252,
           fill=(120, 100, 190, 48), width=max(2, int(S * 0.0028)))
    _soft(img, fr, S * 0.006)

    # -- the keeper's binding, burned down to embers -----------------------
    Rg = R * 1.13
    ember_a0, ember_a1 = 95, 226           # lower-left sweep
    hairline = _layer(S, GOLD)
    hd = ImageDraw.Draw(hairline)
    for s0, s1 in ((ember_a0, ember_a0 + 52), (ember_a0 + 74, ember_a1)):
        hd.arc((cx - Rg, cy - Rg, cx + Rg, cy + Rg), start=s0, end=s1,
               fill=GOLD + (58,), width=max(2, int(S * 0.0028)))
    _soft(img, hairline, S * 0.0035)
    dust = _layer(S, GOLD)
    dd = ImageDraw.Draw(dust)
    brights = []
    for _ in range(22):
        ang = rnd.uniform(ember_a0 - 6, ember_a1 + 8)
        rr = Rg + rnd.gauss(0, R * 0.028)
        x, y = _pt(cx, cy, rr, ang)
        r0 = S * rnd.uniform(0.0016, 0.0052)
        al = int(rnd.uniform(80, 230))
        dd.ellipse((x - r0, y - r0, x + r0, y + r0), fill=GOLD + (al,))
        if rnd.random() < 0.22:
            brights.append((x, y, r0))
    _soft(img, dust, S * 0.005)
    brights = [b for i, b in enumerate(brights) if i != 1]
    for x, y, r0 in brights[:2]:
        bloom = _layer(S, (255, 226, 150))
        bd3 = ImageDraw.Draw(bloom)
        bd3.ellipse((x - r0 * 4, y - r0 * 4, x + r0 * 4, y + r0 * 4),
                    fill=(255, 226, 150, 150))
        _soft(img, bloom, S * 0.008)
        d.ellipse((x - r0 * 0.9, y - r0 * 0.9, x + r0 * 0.9, y + r0 * 0.9),
                  fill=(255, 236, 190, 255))

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
