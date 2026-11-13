#!/usr/bin/env python3
"""news-image-01 -- one image summing up the world news of Friday 13 November 2026.

A newspaper front page drawn from scratch in pure Python 3.13 standard
library: a hand-rolled 5x7 bitmap font, flat vector shapes, a zlib PNG
encoder written by hand. Deterministic (fixed-seed LCG for the city
lights), no network, no files read, no timestamps. Writes a 1024x1024
PNG (<= 1 MiB) to $MAKEFUN_OUTPUT_DIR/entry.png (default ./out/entry.png).

Stories pictured (all from the news of 13 November 2026):
  Lead   -- Ukraine peace talks: US envoys Witkoff & Kushner met Putin in
            Moscow; Putin agreed Europe joins the next round; Zelensky met
            the envoys in Dublin; a large prisoner exchange agreed.
  Vignettes -- Nvidia CEO Jensen Huang resigns (shares down ~4%);
            Microsoft 365 global outage (Outlook, Teams, Copilot, 74
            countries); Israeli strike on Nasser Hospital, Khan Younis,
            kills six; Ukrainian drone hits a Russian warship in the Gulf
            of Finland; FBI: North Korean hackers stole $400m in crypto
            via fake video calls; Harry Kane breaks England's appearance
            record (126 caps) vs Croatia.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER   = (247, 243, 232)   # newsprint cream
INK     = (24, 24, 24)
RULE    = (178, 172, 156)   # light separator
NAVY    = (16, 42, 90)
NIGHT   = (10, 28, 66)      # globe night side
SEABLUE = (24, 58, 110)
LAND    = (38, 92, 66)
LIGHT   = (255, 214, 90)    # city lights
WHITE   = (255, 255, 255)
RED     = (196, 30, 30)
YELLOW  = (245, 200, 40)
GREY    = (120, 120, 120)
DGREY   = (70, 70, 70)
LGREY   = (150, 150, 150)
GREEN   = (46, 125, 50)
DGREEN  = (24, 77, 32)
ORANGE  = (235, 120, 30)
SKIN    = (232, 190, 150)
GOLD    = (212, 175, 55)
DGOLD   = (150, 115, 25)
BROWN   = (120, 72, 20)
UKRBLUE = (0, 87, 183)
UKRYEL  = (255, 213, 0)
EUBLUE  = (0, 51, 153)
SCREEN  = (18, 20, 34)

# ------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells ('#' = ink). Hand-defined from scratch.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '$': ("00100", "01111", "10101", "01110", "00101", "11110", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * (6 * scale) - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)
        self.rect(0, 0, W, H, PAPER)

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def outline(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for y in range(-r, r + 1):
            dx = int((r * r - y * y) ** 0.5)
            self.rect(cx - dx, cy + y, 2 * dx + 1, 1, c)

    def circle_outline(self, cx, cy, r, c, t=1):
        for k in range(t):
            rr = r - k
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(-ry, ry + 1):
            dx = int(rx * (1 - (y * y) / float(ry * ry)) ** 0.5) if ry else 0
            self.rect(cx - dx, cy + y, 2 * dx + 1, 1, c)

    def triangle(self, p1, p2, p3, c):
        ys = [p1[1], p2[1], p3[1]]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for a, b in ((p1, p2), (p2, p3), (p3, p1)):
                if a[1] == b[1]:
                    continue
                if min(a[1], b[1]) <= y < max(a[1], b[1]):
                    t = (y - a[1]) / (b[1] - a[1])
                    xs.append(a[0] + t * (b[0] - a[0]))
            if len(xs) >= 2:
                x0, x1 = int(min(xs)), int(max(xs))
                self.rect(x0, y, x1 - x0 + 1, 1, c)

    def text(self, x, y, s, scale, c, align="left"):
        if align == "center":
            x -= text_width(s, scale) // 2
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale


# ------------------------------------------------------- deterministic rng
def lcg(seed):
    s = seed
    while True:
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        yield s


# ------------------------------------------------------------------ dove
def draw_dove(cv):
    # White dove flying right, olive branch in its beak, above the globe.
    # Neck + raised head so it reads as a bird, not a fish; tail feathers
    # sweep down-left, wing arcs over the back.
    cv.triangle((466, 178), (432, 196), (462, 198), WHITE)  # tail feather 1
    cv.triangle((466, 188), (438, 206), (466, 200), WHITE)  # tail feather 2
    cv.ellipse(505, 186, 48, 18, WHITE)          # body
    cv.ellipse(540, 172, 13, 11, WHITE)          # neck
    cv.circle(556, 160, 15, WHITE)               # head, raised
    cv.triangle((570, 156), (590, 162), (570, 166), ORANGE)  # beak
    cv.rect(560, 155, 3, 3, INK)                 # eye
    cv.ellipse(494, 176, 28, 9, (214, 214, 214))  # wing
    cv.ellipse(494, 178, 20, 5, (196, 196, 196))  # wing shading
    # Olive branch held in the beak, drooping down-right.
    cv.line(588, 164, 626, 194, DGREEN)
    cv.line(589, 164, 627, 194, DGREEN)
    cv.ellipse(600, 174, 9, 4, GREEN)
    cv.ellipse(612, 184, 9, 4, GREEN)
    cv.ellipse(606, 190, 4, 9, GREEN)
    cv.circle(618, 192, 4, DGREEN)
    cv.circle(626, 198, 4, DGREEN)


# ------------------------------------------------------------------ flags
def draw_flag_ukraine(cv, x, y, w, h):
    cv.rect(x, y, w, h // 2, UKRBLUE)
    cv.rect(x, y + h // 2, w, h - h // 2, UKRYEL)
    cv.outline(x, y, w, h, INK, 2)


def draw_flag_eu(cv, x, y, w, h):
    import math
    cv.rect(x, y, w, h, EUBLUE)
    cx, cy, r = x + w // 2, y + h // 2, 13
    for k in range(12):
        a = math.radians(k * 30 - 90)
        cv.circle(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), 2, YELLOW)
    cv.outline(x, y, w, h, INK, 2)


def draw_flag_usa(cv, x, y, w, h):
    stripe = h // 7
    for i in range(7):
        cv.rect(x, y + i * stripe, w, stripe, RED if i % 2 == 0 else WHITE)
    cv.rect(x, y, w * 2 // 5, stripe * 4, NAVY)
    for row in range(3):
        for col in range(4):
            cv.set(x + 5 + col * 7, y + 4 + row * 6, WHITE)
    cv.outline(x, y, w, h, INK, 2)


# ------------------------------------------------------------------ globe
def draw_globe(cv):
    cx, cy, r = 512, 352, 132
    cv.circle(cx, cy, r, NIGHT)
    cv.circle_outline(cx, cy, r, (70, 120, 190), 3)
    # Landmasses in dark green, night side.
    cv.ellipse(468, 318, 46, 24, LAND)
    cv.ellipse(560, 382, 52, 28, LAND)
    cv.ellipse(478, 412, 30, 18, LAND)
    cv.ellipse(592, 300, 24, 15, LAND)
    cv.ellipse(520, 340, 22, 14, LAND)
    # City lights: fixed-seed deterministic scatter inside the globe.
    rng = lcg(20261113)
    placed = 0
    while placed < 150:
        dx = next(rng) % (2 * r) - r
        dy = next(rng) % (2 * r) - r
        if dx * dx + dy * dy > (r - 8) * (r - 8):
            continue
        cv.rect(cx + dx, cy + dy, 2, 2, LIGHT)
        placed += 1
    # Thin daylight crescent on the right rim.
    cv.circle_outline(cx, cy, r - 4, (120, 170, 230), 2)


# -------------------------------------------------------------- vignettes
def v_nvidia(cv, x, y):
    # Empty witness chair, computer chip, red downward arrow.
    cv.rect(x + 58, y + 8, 10, 58, BROWN)        # chair back
    cv.rect(x + 40, y + 64, 80, 10, BROWN)       # seat
    cv.rect(x + 46, y + 74, 7, 22, BROWN)        # legs
    cv.rect(x + 108, y + 74, 7, 22, BROWN)
    cv.rect(x + 185, y + 22, 64, 64, (28, 28, 28))  # chip
    for i in range(4):                            # pins
        cv.rect(x + 193 + i * 14, y + 14, 6, 8, DGREY)
        cv.rect(x + 193 + i * 14, y + 86, 6, 8, DGREY)
        cv.rect(x + 177, y + 30 + i * 14, 8, 6, DGREY)
        cv.rect(x + 249, y + 30 + i * 14, 8, 6, DGREY)
    cv.rect(x + 205, y + 42, 24, 24, (96, 96, 96))
    cv.rect(x + 340, y + 10, 10, 52, RED)        # arrow shaft
    cv.triangle((x + 322, y + 58), (x + 368, y + 58), (x + 345, y + 84), RED)


def v_microsoft(cv, x, y):
    # Dark envelope with a warning triangle.
    cv.rect(x + 150, y + 18, 170, 86, (45, 55, 75))
    cv.line(x + 150, y + 18, x + 235, y + 62, (90, 100, 125))
    cv.line(x + 320, y + 18, x + 235, y + 62, (90, 100, 125))
    cv.line(x + 150, y + 104, x + 235, y + 62, (90, 100, 125))
    cv.line(x + 320, y + 104, x + 235, y + 62, (90, 100, 125))
    cv.triangle((x + 235, y + 26), (x + 203, y + 88), (x + 267, y + 88), YELLOW)
    cv.rect(x + 233, y + 46, 5, 22, INK)         # exclamation mark
    cv.rect(x + 233, y + 72, 5, 5, INK)


def v_hospital(cv, x, y):
    # Hospital building with a cross, plus a lit candle.
    cv.rect(x + 140, y + 18, 130, 86, WHITE)
    cv.outline(x + 140, y + 18, 130, 86, DGREY, 2)
    cv.rect(x + 192, y + 0, 26, 26, RED)         # cross sign
    cv.rect(x + 202, y + 4, 6, 18, WHITE)
    cv.rect(x + 197, y + 9, 16, 6, WHITE)
    for row in range(3):
        for col in range(3):
            cv.rect(x + 152 + col * 40, y + 32 + row * 22, 18, 14, (60, 80, 110))
    cv.rect(x + 196, y + 84, 18, 20, DGREY)      # door
    cv.rect(x + 312, y + 58, 10, 44, WHITE)      # candle
    cv.outline(x + 312, y + 58, 10, 44, DGREY, 1)
    cv.ellipse(x + 317, y + 48, 6, 10, ORANGE)   # flame
    cv.ellipse(x + 317, y + 50, 3, 5, YELLOW)


def v_warship(cv, x, y):
    # Grey warship with smoke, on a grey sea.
    cv.rect(x + 20, y + 80, 420, 20, (96, 116, 134))   # sea
    cv.line(x + 40, y + 88, x + 120, y + 88, WHITE)
    cv.line(x + 300, y + 94, x + 400, y + 94, WHITE)
    cv.circle(x + 238, y + 16, 9, LGREY)         # smoke
    cv.circle(x + 254, y + 8, 11, LGREY)
    cv.circle(x + 272, y + 4, 8, LGREY)
    cv.rect(x + 232, y + 26, 18, 14, DGREY)      # funnel
    cv.rect(x + 180, y + 40, 92, 16, DGREY)      # superstructure
    cv.line(x + 220, y + 40, x + 220, y + 22, DGREY)  # mast
    cv.rect(x + 120, y + 56, 220, 24, GREY)      # hull
    cv.triangle((x + 340, y + 56), (x + 340, y + 80), (x + 372, y + 80), GREY)
    cv.rect(x + 120, y + 56, 220, 4, (150, 150, 150))


def v_hack(cv, x, y):
    # Laptop showing a masked face, gold coins spilling out.
    cv.rect(x + 150, y + 10, 150, 84, SCREEN)
    cv.outline(x + 150, y + 10, 150, 84, INK, 2)
    cv.circle(x + 225, y + 52, 26, SKIN)         # face
    cv.rect(x + 199, y + 42, 52, 13, INK)        # black mask band
    cv.circle(x + 213, y + 48, 3, WHITE)         # eyes
    cv.circle(x + 237, y + 48, 3, WHITE)
    cv.rect(x + 135, y + 94, 180, 8, DGREY)      # laptop base
    for cx, cy, r in ((300, 97, 6), (316, 100, 6), (288, 100, 5),
                      (330, 97, 5), (308, 102, 5), (324, 103, 5)):
        cv.circle(x + cx, y + cy, r, GOLD)
        cv.circle_outline(x + cx, y + cy, r, DGOLD, 1)


def v_kane(cv, x, y):
    # Footballer in a white shirt, arms raised, with a football.
    cv.circle(x + 212, y + 30, 14, SKIN)         # head
    for d in (-1, 0, 1):  # raised arms, thickened
        cv.line(x + 200 + d, y + 48, x + 178 + d, y + 22, INK)
        cv.line(x + 224 + d, y + 48, x + 246 + d, y + 22, INK)
    cv.rect(x + 196, y + 46, 32, 46, WHITE)      # white shirt
    cv.outline(x + 196, y + 46, 32, 46, DGREY, 1)
    cv.rect(x + 200, y + 92, 9, 14, INK)         # legs
    cv.rect(x + 215, y + 92, 9, 14, INK)
    cv.circle(x + 330, y + 46, 20, WHITE)        # football
    cv.circle_outline(x + 330, y + 46, 20, INK, 2)
    cv.circle(x + 330, y + 46, 5, INK)           # pentagon
    for dx, dy in ((-12, -8), (12, -8), (-12, 10), (12, 10), (0, -15)):
        cv.circle(x + 330 + dx, y + 46 + dy, 2, INK)


VIGNETTES = [
    (v_nvidia,    "NVIDIA CEO RESIGNS"),
    (v_microsoft, "MICROSOFT OUTAGE"),
    (v_hospital,  "HOSPITAL STRIKE KILLS SIX"),
    (v_warship,   "DRONE HITS RUSSIAN WARSHIP"),
    (v_hack,      "FBI: N. KOREA $400M HACK"),
    (v_kane,      "KANE BREAKS ENGLAND RECORD"),
]


# -------------------------------------------------------------- front page
def draw_front_page(cv):
    # Masthead.
    cv.text(512, 24, "13 NOVEMBER 2026", 8, INK, align="center")
    cv.text(512, 90, "THE WORLD TODAY", 4, INK, align="center")
    cv.rect(40, 130, 944, 3, INK)
    cv.rect(40, 136, 944, 1, INK)

    # Lead story: dove, globe, flags, banner.
    draw_dove(cv)
    draw_globe(cv)
    draw_flag_ukraine(cv, 690, 248, 72, 44)
    draw_flag_eu(cv, 690, 300, 72, 44)
    draw_flag_usa(cv, 690, 352, 72, 44)
    cv.rect(212, 500, 600, 42, NAVY)
    cv.text(512, 511, "EUROPE JOINS UKRAINE TALKS", 3, WHITE, align="center")

    # Six vignettes in a 2x3 grid.
    cols_x = (40, 524)
    rows_y = (560, 700, 840)
    for i, (fn, label) in enumerate(VIGNETTES):
        x = cols_x[i % 2]
        y = rows_y[i // 2]
        fn(cv, x, y)
        cv.text(x + 230, y + 108, label, 2, INK, align="center")
    cv.line(512, 556, 512, 978, RULE)
    cv.line(40, 694, 984, 694, RULE)
    cv.line(40, 834, 984, 834, RULE)

    # Footer.
    cv.rect(40, 982, 944, 2, RULE)
    cv.text(512, 992, "FRIDAY 13 NOVEMBER 2026 - WORLD NEWS IN ONE IMAGE",
            2, DGREY, align="center")


# -------------------------------------------------------------------- png
def write_png(path, px):
    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    path = os.path.join(out_dir, "entry.png")
    cv = Canvas()
    draw_front_page(cv)
    write_png(path, cv.px)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
