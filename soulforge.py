"""The Soulforge — renders the Soulkeep sigil (a faceted soulstone holding a
captured soul-wisp, bound by gold keeper's claws) at any size.

Run directly to regenerate icon-512.png / icon-192.png / icon.ico;
app.py imports draw_sigil() for the brag card.
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


def draw_sigil(size, pad_frac=0.0):
    """Return an RGBA Image of the sigil. Renders 4x supersampled."""
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S / 2
    R = S * (0.5 - pad_frac) * 0.68  # stone radius

    # -- ambient halo ------------------------------------------------------
    halo = Image.new("RGBA", (S, S), GLOW + (0,))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((cx - R * 1.22, cy - R * 1.22, cx + R * 1.22, cy + R * 1.22), fill=GLOW + (72,))
    halo = halo.filter(ImageFilter.GaussianBlur(S * 0.035))
    img.alpha_composite(halo)

    d = ImageDraw.Draw(img)

    # -- stone: 8 full wedge facets, lit from the upper-left ---------------
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=STONE_DARK + (255,))
    for i in range(8):
        a0 = -112.5 + i * 45
        mid = math.radians(a0 + 22.5)
        lit = (math.cos(mid - math.radians(-135)) + 1) / 2  # 1 facing up-left
        base = (
            int(50 + 60 * lit),
            int(31 + 42 * lit),
            int(110 + 110 * lit),
        )
        d.pieslice((cx - R, cy - R, cx + R, cy + R), start=a0, end=a0 + 45,
                   fill=base + (255,))
    # luminous core rising from the gem's depths
    core = Image.new("RGBA", (S, S), (116, 74, 208, 0))
    cd = ImageDraw.Draw(core)
    cd.ellipse((cx - R * 0.56, cy - R * 0.56, cx + R * 0.56, cy + R * 0.56),
               fill=(116, 74, 208, 200))
    core2 = Image.new("RGBA", (S, S), (158, 112, 244, 0))
    cd2 = ImageDraw.Draw(core2)
    cd2.ellipse((cx - R * 0.34, cy - R * 0.34, cx + R * 0.34, cy + R * 0.34),
                fill=(158, 112, 244, 210))
    # facet seams: faint hairlines in the outer band only
    for i in range(8):
        a0 = -112.5 + i * 45
        d.line([_pt(cx, cy, R * 0.58, a0), _pt(cx, cy, R * 0.97, a0)],
               fill=(216, 190, 255, 60), width=max(2, S // 400))
    img.alpha_composite(core.filter(ImageFilter.GaussianBlur(S * 0.035)))
    img.alpha_composite(core2.filter(ImageFilter.GaussianBlur(S * 0.035)))

    # -- the kept soul: a comma-wisp spiraling into the heart --------------
    soul = Image.new("RGBA", (S, S), TEAL + (0,))
    sd = ImageDraw.Draw(soul)
    hx, hy = cx - R * 0.10, cy - R * 0.08          # heart sits just off-center
    steps = 72
    for i in range(steps):
        t = i / (steps - 1)
        ang = -30 + t * 265                         # tail sweeps clockwise from upper-right
        rr = R * (0.15 + 0.40 * t)                  # spiraling outward as it trails
        w = (1 - t) ** 1.5 * R * 0.135 + R * 0.010
        x, y = _pt(hx, hy, rr, ang)
        a = int(245 * (1 - t) ** 0.55 + 10)
        sd.ellipse((x - w, y - w, x + w, y + w), fill=TEAL + (a,))
    img.alpha_composite(soul.filter(ImageFilter.GaussianBlur(S * 0.003)))
    # a clean lavender halo just around the head keeps the glow un-muddy
    hal = Image.new("RGBA", (S, S), (210, 245, 235, 0))
    hd3 = ImageDraw.Draw(hal)
    hd3.ellipse((hx - R * 0.24, hy - R * 0.24, hx + R * 0.24, hy + R * 0.24),
                fill=(210, 245, 235, 88))
    img.alpha_composite(hal.filter(ImageFilter.GaussianBlur(S * 0.018)))
    d = ImageDraw.Draw(img)
    # star-souls kept in the stone's darker sky
    for sr, sa, sz2, al in ((0.74, 12, 0.014, 235), (0.62, 48, 0.009, 190),
                            (0.80, 66, 0.011, 210), (0.55, 96, 0.008, 165),
                            (0.72, 118, 0.012, 220), (0.85, 38, 0.007, 150)):
        x, y = _pt(cx, cy, R * sr, sa)
        rr2 = S * sz2 / 2
        d.ellipse((x - rr2, y - rr2, x + rr2, y + rr2), fill=INK + (al,))
    # heart of the soul
    hr = R * 0.165
    d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=TEAL + (255,))
    d.ellipse((hx - hr * 0.55, hy - hr * 0.62, hx + hr * 0.25, hy + hr * 0.18),
              fill=TEAL_HI + (255,))

    # -- glints on the lit facets ------------------------------------------
    for gr, ga, gl in ((0.80, -150, 0.10), (0.72, -104, 0.055)):
        gx, gy = _pt(cx, cy, R * gr, ga)
        ll = R * gl
        d.line([_pt(gx, gy, ll, 45), _pt(gx, gy, ll, 225)], fill=(255, 255, 255, 200),
               width=max(2, S // 400))
        d.line([_pt(gx, gy, ll * 0.5, 135), _pt(gx, gy, ll * 0.5, 315)],
               fill=(255, 255, 255, 200), width=max(2, S // 400))

    # -- rim ---------------------------------------------------------------
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=VIOLET + (230,),
              width=max(3, S // 170))
    d.arc((cx - R, cy - R, cx + R, cy + R), start=175, end=250,
          fill=INK + (230,), width=max(2, S // 300))

    # -- gold keeper's claws: two crescents gripping the stone -------------
    Rc = R * 1.17
    cw = max(4, int(S * 0.022))
    box = (cx - Rc, cy - Rc, cx + Rc, cy + Rc)
    d.arc(box, start=-58, end=32, fill=GOLD + (255,), width=cw)
    d.arc(box, start=122, end=212, fill=GOLD + (255,), width=cw)
    for tip in (-58, 32, 122, 212):
        x0, y0 = _pt(cx, cy, Rc, tip)
        x1, y1 = _pt(cx, cy, R * 1.035, tip)
        d.line([(x0, y0), (x1, y1)], fill=GOLD + (255,), width=cw)

    # -- spark where the light kisses the claw -----------------------------
    sx, sy = _pt(cx, cy, Rc, 208)
    sl = S * 0.038
    for ang, ll in ((0, sl), (90, sl), (45, sl * 0.45), (135, sl * 0.45)):
        x0, y0 = _pt(sx, sy, ll, ang)
        x1, y1 = _pt(sx, sy, ll, ang + 180)
        d.line([(x0, y0), (x1, y1)], fill=INK + (240,), width=max(2, S // 300))
    d.ellipse((sx - S * 0.006, sy - S * 0.006, sx + S * 0.006, sy + S * 0.006),
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
