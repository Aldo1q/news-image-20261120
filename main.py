#!/usr/bin/env python3
"""THE DAILY LEDGER - one-image broadsheet front page for Friday 20 November 2026.

Draws a deterministic 1024x1024 newspaper front page with Pillow:
masthead, a markets band, the AI-selloff lead with a drawn hero panel
(plunging red chart over a night skyline), four world briefs and a
bottom news ticker. No network, no randomness beyond a fixed seed,
so every run writes byte-identical output.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width

PAPER = (248, 244, 231)
INK = (24, 22, 18)
FAINT = (108, 100, 84)
RULE = (24, 22, 18)
RED = (178, 30, 24)
BAND_BG = (16, 16, 18)
DOWN = (255, 92, 76)
UP = (94, 214, 120)
BAND_TXT = (238, 236, 228)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def centered(draw, cx, y, s, fnt, fill=INK):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def rule(draw, x0, x1, y, wdt=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=wdt)


# ---------------------------------------------------------------- markets band
MARKETS = [
    [("S&P 500", "7,175.83", "-2.02%", DOWN),
     ("NASDAQ", "23,879.20", "-2.25%", DOWN),
     ("NIKKEI", "56,562", "-4.85%", DOWN),
     ("VIX", "28.44", "+15.8%", UP)],
    [("GOLD", "$3,531", "-4.2%", DOWN),
     ("BRENT", "$92.77", "+0.9%", UP),
     ("BITCOIN", "$61,828", "-2.5%", DOWN),
     ("ANTHROPIC", "$97.17", "+17.1%", UP)],
]


def draw_markets(draw, y):
    h = 60
    draw.rectangle([MARGIN, y, W - MARGIN, y + h], fill=BAND_BG)
    f_lab = font(SANS_B, 13)
    f_val = font(SANS_B, 16)
    col_w = CW / 4
    for r, row in enumerate(MARKETS):
        ry = y + 5 + r * 28
        for c, (lab, val, pct, col) in enumerate(row):
            x = MARGIN + c * col_w + 12
            draw.text((x, ry + 2), lab, font=f_lab, fill=(168, 164, 152))
            vx = x + text_w(draw, lab, f_lab) + 8
            draw.text((vx, ry), val, font=f_val, fill=BAND_TXT)
            px = vx + text_w(draw, val, f_val) + 8
            draw.text((px, ry), pct, font=f_val, fill=col)
    return y + h


# ------------------------------------------------------------------- hero art
class Lcg:
    """Tiny deterministic pseudo-random source (fixed seed per run)."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF

    def next(self, mod):
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state % mod


def draw_hero(img, x0, y0, x1, y1):
    """Plunging red index chart over a two-layer night skyline."""
    d = ImageDraw.Draw(img, "RGBA")
    hh = y1 - y0
    # night sky gradient
    for i in range(hh):
        t = i / max(1, hh - 1)
        col = (int(10 + 14 * t), int(14 + 22 * t), int(34 + 44 * t))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=col + (255,))
    rng = Lcg(20261120)
    # stars
    for _ in range(60):
        sx = x0 + rng.next(x1 - x0)
        sy = y0 + rng.next(hh // 2)
        d.point((sx, sy), fill=(210, 216, 235, 160))
    # far skyline
    bx = x0
    while bx < x1:
        bw = 26 + rng.next(38)
        bh = 40 + rng.next(50)
        d.rectangle([bx, y1 - bh, bx + bw - 3, y1], fill=(16, 22, 44, 255))
        bx += bw
    # near skyline with lit windows (kept low so the chart stays readable)
    bx = x0 - 8
    while bx < x1:
        bw = 34 + rng.next(52)
        bh = 58 + rng.next(64)
        top = y1 - bh
        d.rectangle([bx, top, bx + bw - 4, y1], fill=(6, 8, 18, 255))
        for wy in range(top + 8, y1 - 8, 11):
            for wx in range(bx + 5, bx + bw - 9, 9):
                if rng.next(10) < 3:
                    d.rectangle([wx, wy, wx + 4, wy + 5],
                                fill=(255, 196, 92, 235))
        bx += bw
    # faint chart grid
    for gx in range(x0 + 60, x1, 96):
        d.line([(gx, y0 + 10), (gx, y1 - 10)], fill=(255, 255, 255, 26))
    for gy in range(y0 + 34, y1, 44):
        d.line([(x0 + 10, gy), (x1 - 10, gy)], fill=(255, 255, 255, 26))
    # the plunge: jagged drift down, then a cliff (starts below the labels)
    pts = []
    n = 26
    for i in range(n + 1):
        t = i / n
        px = x0 + 26 + t * (x1 - x0 - 90)
        base = y0 + 74 + t * t * (hh - 168)
        jig = ((i * 37) % 13) - 6
        pts.append((px, base + jig))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(pts, fill=(255, 46, 32, 70), width=13)
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.line(pts, fill=(255, 52, 38, 255), width=5)
    for px, py in pts[::5]:
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 120, 100, 255))
    # arrowhead at the end of the plunge
    ex, ey = pts[-1]
    d.polygon([(ex + 26, ey + 20), (ex - 4, ey + 16), (ex + 8, ey - 8)],
              fill=(255, 52, 38, 255))
    # chart labels
    f_big = font(SANS_B, 32)
    d.text((x0 + 22, y0 + 14), "S&P 500  -2.02%", font=f_big,
           fill=(255, 255, 255, 255))
    f_sm = font(SANS_B, 18)
    d.text((x0 + 24, y0 + 52), "SIXTH STRAIGHT LOSS - 7,175.83",
           font=f_sm, fill=(196, 204, 226, 255))
    # translucent strip along the foot of the panel keeps the caption legible
    d.rectangle([x0, y1 - 34, x1, y1], fill=(4, 6, 14, 190))
    tag = "NIKKEI -4.85%"
    tw = d.textlength(tag, font=f_sm)
    d.text((x1 - tw - 20, y1 - 27), tag, font=f_sm, fill=(255, 120, 100, 255))
    cap = "Six down days: the AI trade unwinds from Wall Street to Tokyo."
    d.text((x0 + 22, y1 - 26), cap, font=font(SERIF_I, 17),
           fill=(226, 228, 236, 255))


# --------------------------------------------------------------------- briefs
BRIEFS = [
    ("ICJ: Genocide Against the Rohingya",
     "The World Court ruled 9-6 that Myanmar committed genocide against "
     "the Rohingya - a first-ever finding against a state."),
    ("Europe Ready to Talk With Russia",
     "After the Shenzhen declaration, Europe offers talks with Russia - "
     "while Britain pledges 1,000+ drones (\u00a3260M) to Ukraine."),
    ("Houthi Missile Damages Riyadh Tower",
     "A Houthi missile damaged the Saudi Public Investment Fund tower "
     "in Riyadh."),
    ("Kenya Discharges Last Ebola Patient",
     "Kenya discharged its last Ebola patient, 37 days after the first "
     "case - a bright note on a grim day."),
]

TICKER = ("GTA 6 LAUNCH SALES TOP $2.3B  \u2022  IAEA: NORTH KOREA EXPANDING "
          "URANIUM ENRICHMENT  \u2022  PENTAGON PUTS IRAN WAR COST AT $48.3B  "
          "\u2022  US CYBER CHIEF OUSTED AFTER OUTAGE WAVE  \u2022  KYIV "
          "BRIDGES HIT IN RUSSIAN STRIKE")


def draw_brief(draw, x, y, wdt, head, body):
    f_h = font(SERIF_B, 22)
    f_b = font(SERIF, 17)
    cy = y
    for ln in wrap(draw, head, f_h, wdt):
        draw.text((x, cy), ln, font=f_h, fill=INK)
        cy += 26
    cy += 3
    for ln in wrap(draw, body, f_b, wdt):
        draw.text((x, cy), ln, font=f_b, fill=(52, 48, 40))
        cy += 21
    return cy


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # page frame: double rule
    d.rectangle([14, 14, W - 14, H - 14], outline=RULE, width=3)
    d.rectangle([22, 22, W - 22, H - 22], outline=RULE, width=1)

    # top strap
    f_strap = font(SANS_B, 15)
    d.text((MARGIN + 4, 33), "LATE CITY EDITION", font=f_strap, fill=INK)
    s = "ONE PAGE - THE WHOLE DAY"
    d.text((W - MARGIN - 4 - text_w(d, s, f_strap), 33), s,
           font=f_strap, fill=INK)
    rule(d, MARGIN, W - MARGIN, 58, 2)

    # masthead
    centered(d, W / 2, 66, "THE DAILY LEDGER", font(SERIF_B, 74))
    rule(d, MARGIN, W - MARGIN, 148, 5)
    rule(d, MARGIN, W - MARGIN, 157, 1)

    # date line
    f_date = font(SANS_B, 20)
    centered(d, W / 2, 165, "FRIDAY, 20 NOVEMBER 2026", f_date, fill=RED)
    f_vol = font(SANS, 14)
    d.text((MARGIN + 4, 168), "Vol. I - No. 324", font=f_vol, fill=FAINT)
    s = "World news, summed up in one image"
    d.text((W - MARGIN - 4 - text_w(d, s, f_vol), 168), s,
           font=f_vol, fill=FAINT)

    # markets band
    y = draw_markets(d, 193)

    # lead headline (one strong line) + standfirst
    y += 14
    centered(d, W / 2, y, "AI SELLOFF ROCKS GLOBAL MARKETS",
             font(SERIF_B, 48))
    y += 62
    f_sub = font(SERIF_I, 23)
    sub = ("S&P 500 slides 2.02% in a sixth straight loss as the Dow closes "
           "below 50,000 - while Anthropic leaps 17.1% on its debut")
    for ln in wrap(d, sub, f_sub, CW - 90):
        centered(d, W / 2, y, ln, f_sub, fill=(52, 48, 40))
        y += 28

    # hero panel (about a quarter of the page)
    y += 6
    hero_h = 246
    draw_hero(img, MARGIN, y, W - MARGIN, y + hero_h)
    d = ImageDraw.Draw(img)
    d.rectangle([MARGIN, y, W - MARGIN, y + hero_h], outline=INK, width=2)
    y += hero_h

    # briefs header
    y += 10
    rule(d, MARGIN, W - MARGIN, y, 2)
    centered(d, W / 2, y + 5, "THE WORLD IN BRIEF", font(SANS_B, 18))
    y += 30
    rule(d, MARGIN, W - MARGIN, y, 1)
    y += 10

    col_w = (CW - 28) / 2
    briefs_top = y
    row1 = max(draw_brief(d, MARGIN, y, col_w, *BRIEFS[0]),
               draw_brief(d, MARGIN + col_w + 28, y, col_w, *BRIEFS[1]))
    y = row1 + 8
    row2 = max(draw_brief(d, MARGIN, y, col_w, *BRIEFS[2]),
               draw_brief(d, MARGIN + col_w + 28, y, col_w, *BRIEFS[3]))
    d.line([(W / 2, briefs_top + 2), (W / 2, row2 - 2)],
           fill=(190, 182, 160), width=1)

    # ticker band pinned near the foot
    ty = H - MARGIN - 68
    d.rectangle([MARGIN, ty, W - MARGIN, ty + 68], fill=BAND_BG)
    f_tick = font(SANS_B, 13)
    lines = wrap(d, TICKER, f_tick, CW - 24)
    ly = ty + 5
    for ln in lines[:4]:
        centered(d, W / 2, ly, ln, f_tick, fill=BAND_TXT)
        ly += 16
    return img


def main():
    img = build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "."
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
