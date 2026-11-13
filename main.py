#!/usr/bin/env python3
"""news-image-01 — one image summing up the world news of Friday 13 November 2026.

A newspaper front page, drawn from scratch with pure Python standard
library only (zlib PNG encoder written by hand, 5x7 bitmap font drawn with
filled rectangles). Deterministic: no network, no files read, no clock, no
unseeded randomness — the only pseudo-randomness comes from a fixed-seed
generator, so two runs produce byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default ./out/entry.png),
1024x1024, well under 1 MiB.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- colours
PAPER = (246, 241, 227)
WHITE = (255, 255, 255)
INK = (18, 18, 18)
NAVY = (16, 32, 64)
NIGHT = (11, 30, 58)
OCEAN = (29, 78, 137)
GOLD = (242, 195, 0)
RED = (198, 32, 32)
GREY = (120, 128, 138)
BORDER = (176, 168, 148)
SKIN = (232, 190, 160)
GREEN = (46, 125, 50)

# ------------------------------------------------------- fixed-seed random
_seed = [987654321]


def rnd():
    _seed[0] = (1103515245 * _seed[0] + 12345) & 0x7FFFFFFF
    return _seed[0]


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self):
        self.buf = bytearray(W * H * 3)
        self.rect(0, 0, W, H, PAPER)

    def px(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = col[0]
            self.buf[i + 1] = col[1]
            self.buf[i + 2] = col[2]

    def rect(self, x, y, w, h, col):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            for xx in range(x0, x1):
                self.buf[i] = col[0]
                self.buf[i + 1] = col[1]
                self.buf[i + 2] = col[2]
                i += 3

    def circle(self, cx, cy, r, col):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, col)

    def ellipse(self, cx, cy, rx, ry, col):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, col)

    def line(self, x0, y0, x1, y1, col):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, col, t=4):
        for ox in range(-t // 2, t // 2 + 1):
            for oy in range(-t // 2, t // 2 + 1):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, col)

    def tri(self, ax, ay, bx, by, cx, cy, col):
        def edge(xa, ya, xb, yb, x, y):
            return (x - xa) * (yb - ya) - (y - ya) * (xb - xa)

        d = edge(ax, ay, bx, by, cx, cy)
        if d == 0:
            return
        minx = max(0, min(ax, bx, cx))
        maxx = min(W - 1, max(ax, bx, cx))
        miny = max(0, min(ay, by, cy))
        maxy = min(H - 1, max(ay, by, cy))
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                w0 = edge(bx, by, cx, cy, x, y)
                w1 = edge(cx, cy, ax, ay, x, y)
                w2 = edge(ax, ay, bx, by, x, y)
                if (d > 0 and w0 >= 0 and w1 >= 0 and w2 >= 0) or \
                   (d < 0 and w0 <= 0 and w1 <= 0 and w2 <= 0):
                    self.px(x, y, col)


# ------------------------------------------------------------- 5x7 font
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, s, x, y, scale, col, center=False):
    if center:
        x -= text_width(s, scale) // 2
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g:
            for row in range(7):
                bits = g[row]
                for ci in range(5):
                    if bits[ci] == "1":
                        cv.rect(cx + ci * scale, y + row * scale,
                                scale, scale, col)
        cx += 6 * scale


# ------------------------------------------------------------------- flags
def flag_ukraine(cv, x, y, w=84, h=56):
    cv.rect(x, y, w, h // 2, (0, 87, 183))
    cv.rect(x, y + h // 2, w, h - h // 2, (255, 215, 0))


def flag_eu(cv, x, y, w=84, h=56):
    cv.rect(x, y, w, h, (0, 51, 153))
    import math
    for i in range(12):
        a = 2 * math.pi * i / 12.0 - math.pi / 2
        sx = x + w // 2 + int(19 * math.cos(a))
        sy = y + h // 2 + int(13 * math.sin(a))
        cv.circle(sx, sy, 2, GOLD)


def flag_usa(cv, x, y, w=84, h=56):
    for i in range(13):
        col = (179, 25, 66) if i % 2 == 0 else WHITE
        cv.rect(x, y + i * h // 13, w, h // 13 + 1, col)
    cv.rect(x, y, int(w * 0.4), int(h * 7 / 13), (10, 49, 97))
    for r in range(4):
        for c in range(5):
            cv.circle(x + 4 + c * 6, y + 4 + r * 6, 1, WHITE)


def flag_pole(cv, x, y, h=56):
    cv.rect(x - 3, y - 6, 2, h + 6, (90, 80, 60))
    cv.circle(x - 2, y - 8, 3, GOLD)


# ------------------------------------------------------------------ globe
def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, (120, 160, 210))          # rim light
    cv.circle(cx, cy, r - 3, NIGHT)                # night side
    # continents, slightly lighter blue
    cv.ellipse(cx - 48, cy - 42, 42, 26, OCEAN)
    cv.ellipse(cx + 52, cy - 30, 34, 22, OCEAN)
    cv.ellipse(cx - 20, cy + 48, 48, 22, OCEAN)
    cv.ellipse(cx + 58, cy + 42, 26, 18, OCEAN)
    cv.ellipse(cx - 70, cy + 8, 18, 30, OCEAN)
    # city lights, fixed-seed deterministic, spread evenly over the disc
    for _ in range(120):
        a = rnd() % 360
        u = rnd() / 2147483648.0
        d = int((r - 12) * (u ** 0.5))
        import math
        x = cx + int(d * math.cos(math.radians(a)))
        y = cy + int(d * math.sin(math.radians(a)))
        if (x - cx) ** 2 + (y - cy) ** 2 < (r - 8) ** 2:
            cv.rect(x, y, 2, 2, GOLD)


def draw_dove(cv):
    # white dove flying above the globe, olive branch in its beak
    cv.tri(462, 168, 500, 158, 470, 190, WHITE)     # tail feathers
    cv.ellipse(512, 176, 54, 26, WHITE)            # body
    cv.circle(558, 156, 15, WHITE)                 # head
    cv.tri(571, 152, 588, 158, 571, 163, (230, 120, 40))  # beak
    cv.circle(562, 152, 2, INK)                    # eye
    cv.ellipse(500, 170, 30, 12, (216, 222, 230))  # folded wing
    cv.thick_line(586, 160, 624, 178, GREEN, 3)    # olive branch
    cv.ellipse(600, 166, 9, 4, GREEN)
    cv.ellipse(612, 172, 9, 4, GREEN)
    cv.ellipse(622, 178, 9, 4, GREEN)
    cv.circle(606, 176, 3, (60, 90, 40))
    cv.circle(618, 182, 3, (60, 90, 40))


# --------------------------------------------------------------- vignettes
def cell(cv, x, y):
    cv.rect(x, y, 320, 224, WHITE)
    cv.rect(x, y, 320, 2, BORDER)
    cv.rect(x, y + 222, 320, 2, BORDER)
    cv.rect(x, y, 2, 224, BORDER)
    cv.rect(x + 318, y, 2, 224, BORDER)


def label(cv, x, y, s):
    draw_text(cv, s, x + 160, y + 192, 2, INK, center=True)


def v_nvidia(cv, ox, oy):
    # empty witness chair, computer chip, red downward arrow
    brown = (120, 72, 32)
    cv.rect(ox + 45, oy + 35, 12, 75, brown)        # chair back
    cv.rect(ox + 45, oy + 105, 85, 12, brown)       # chair seat
    cv.rect(ox + 48, oy + 117, 10, 45, brown)       # back leg
    cv.rect(ox + 118, oy + 117, 10, 45, brown)      # front leg
    cv.rect(ox + 150, oy + 55, 70, 70, (30, 30, 40))  # chip
    cv.rect(ox + 162, oy + 67, 46, 46, (70, 80, 110))
    cv.rect(ox + 172, oy + 77, 26, 26, (150, 170, 200))
    for i in range(4):                              # chip pins
        cv.rect(ox + 158 + i * 16, oy + 47, 8, 8, GREY)
        cv.rect(ox + 158 + i * 16, oy + 125, 8, 8, GREY)
        cv.rect(ox + 142, oy + 63 + i * 16, 8, 8, GREY)
        cv.rect(ox + 220, oy + 63 + i * 16, 8, 8, GREY)
    cv.rect(ox + 252, oy + 35, 16, 75, RED)         # arrow shaft
    cv.tri(ox + 232, oy + 110, ox + 288, oy + 110, ox + 260, oy + 158, RED)


def v_microsoft(cv, ox, oy):
    # dark envelope with a warning triangle
    cv.rect(ox + 55, oy + 55, 190, 105, (28, 38, 66))
    cv.line(ox + 55, oy + 55, ox + 150, oy + 110, (96, 116, 165))
    cv.line(ox + 245, oy + 55, ox + 150, oy + 110, (96, 116, 165))
    cv.line(ox + 55, oy + 160, ox + 150, oy + 110, (96, 116, 165))
    cv.line(ox + 245, oy + 160, ox + 150, oy + 110, (96, 116, 165))
    cv.tri(ox + 225, oy + 12, ox + 268, oy + 12, ox + 246, oy + 56, GOLD)
    cv.rect(ox + 243, oy + 22, 6, 16, INK)
    cv.rect(ox + 243, oy + 42, 6, 6, INK)


def v_hospital(cv, ox, oy):
    # hospital building with a cross, lit candle beside it
    cv.rect(ox + 45, oy + 50, 150, 115, WHITE)
    cv.rect(ox + 45, oy + 50, 150, 3, GREY)
    cv.rect(ox + 45, oy + 50, 3, 115, GREY)
    cv.rect(ox + 192, oy + 50, 3, 115, GREY)
    cv.rect(ox + 45, oy + 162, 150, 3, GREY)
    for wx in (ox + 60, ox + 155):
        for wy in (oy + 70, oy + 100):
            cv.rect(wx, wy, 22, 16, (90, 140, 190))
    cv.rect(ox + 112, oy + 62, 12, 36, RED)         # cross
    cv.rect(ox + 100, oy + 72, 36, 12, RED)
    cv.rect(ox + 106, oy + 132, 28, 33, (60, 60, 70))  # door
    cv.rect(ox + 238, oy + 100, 18, 65, WHITE)      # candle
    cv.rect(ox + 238, oy + 100, 18, 2, GREY)
    cv.rect(ox + 238, oy + 100, 2, 65, GREY)
    cv.rect(ox + 254, oy + 100, 2, 65, GREY)
    cv.line(ox + 247, oy + 100, ox + 247, oy + 92, INK)
    cv.ellipse(ox + 247, oy + 82, 8, 13, (240, 140, 0))  # flame
    cv.ellipse(ox + 247, oy + 85, 4, 7, GOLD)


def v_warship(cv, ox, oy):
    # grey warship with smoke on a grey sea
    cv.rect(ox + 10, oy + 125, 300, 45, (125, 140, 155))
    cv.rect(ox + 55, oy + 100, 210, 25, (70, 78, 88))   # hull
    cv.tri(ox + 265, oy + 100, ox + 302, oy + 100, ox + 265, oy + 125,
           (70, 78, 88))                                # bow
    cv.rect(ox + 105, oy + 72, 100, 28, (95, 103, 115))  # superstructure
    cv.rect(ox + 120, oy + 58, 40, 14, (95, 103, 115))   # bridge
    cv.line(ox + 190, oy + 30, ox + 190, oy + 72, (50, 55, 65))  # mast
    cv.rect(ox + 215, oy + 78, 18, 22, (50, 55, 65))    # funnel
    cv.circle(ox + 224, oy + 62, 10, (165, 170, 175))   # smoke
    cv.circle(ox + 234, oy + 46, 12, (175, 180, 185))
    cv.circle(ox + 222, oy + 28, 9, (185, 190, 195))
    cv.line(ox + 30, oy + 140, ox + 90, oy + 140, WHITE)
    cv.line(ox + 130, oy + 152, ox + 200, oy + 152, WHITE)
    cv.line(ox + 220, oy + 140, ox + 290, oy + 140, WHITE)


def v_hack(cv, ox, oy):
    # laptop showing a masked face, gold coins spilling out
    cv.rect(ox + 65, oy + 35, 180, 105, (25, 28, 38))
    cv.rect(ox + 75, oy + 45, 160, 85, (45, 52, 70))
    cv.circle(ox + 155, oy + 85, 26, SKIN)              # face
    cv.rect(ox + 132, oy + 76, 46, 18, (18, 18, 26))    # mask
    cv.rect(ox + 140, oy + 81, 8, 5, WHITE)             # eyes
    cv.rect(ox + 162, oy + 81, 8, 5, WHITE)
    cv.rect(ox + 50, oy + 140, 210, 12, (120, 125, 135))  # base
    for (cx, cy, r) in ((ox + 238, oy + 152, 12), (ox + 262, oy + 160, 12),
                        (ox + 220, oy + 164, 10), (ox + 250, oy + 170, 9)):
        cv.circle(cx, cy, r, GOLD)
        cv.circle(cx, cy, r - 4, (200, 160, 0))


def v_kane(cv, ox, oy):
    # footballer in a white shirt raising his arms, football beside him
    cv.circle(ox + 150, oy + 50, 15, SKIN)              # head
    cv.rect(ox + 135, oy + 66, 30, 42, WHITE)           # shirt
    cv.rect(ox + 135, oy + 66, 30, 3, GREY)
    cv.rect(ox + 135, oy + 66, 3, 42, GREY)
    cv.rect(ox + 162, oy + 66, 3, 42, GREY)
    cv.rect(ox + 137, oy + 108, 26, 16, NAVY)           # shorts
    cv.rect(ox + 140, oy + 124, 8, 30, INK)             # legs
    cv.rect(ox + 154, oy + 124, 8, 30, INK)
    cv.thick_line(ox + 138, oy + 72, ox + 112, oy + 40, SKIN, 5)  # arms up
    cv.thick_line(ox + 162, oy + 72, ox + 188, oy + 40, SKIN, 5)
    cv.circle(ox + 112, oy + 38, 5, SKIN)               # hands
    cv.circle(ox + 188, oy + 38, 5, SKIN)
    cv.circle(ox + 228, oy + 58, 20, (200, 205, 210))   # ball rim
    cv.circle(ox + 228, oy + 58, 18, WHITE)             # ball
    cv.circle(ox + 228, oy + 58, 5, INK)
    cv.circle(ox + 214, oy + 46, 3, INK)
    cv.circle(ox + 242, oy + 46, 3, INK)
    cv.circle(ox + 214, oy + 70, 3, INK)
    cv.circle(ox + 242, oy + 70, 3, INK)


# -------------------------------------------------------------------- page
def draw_page():
    cv = Canvas()
    # outer frame
    cv.rect(8, 8, 1008, 3, INK)
    cv.rect(8, 1013, 1008, 3, INK)
    cv.rect(8, 8, 3, 1008, INK)
    cv.rect(1013, 8, 3, 1008, INK)

    # masthead
    draw_text(cv, "13 NOVEMBER 2026", 512, 30, 6, INK, center=True)
    draw_text(cv, "THE WORLD TODAY", 512, 88, 3, INK, center=True)
    cv.rect(40, 120, 944, 4, INK)
    cv.rect(40, 128, 944, 2, INK)

    # lead story: globe first, dove flying in front of it, flags, banner
    draw_globe(cv, 512, 308, 126)
    draw_dove(cv)
    flag_pole(cv, 150, 230)
    flag_ukraine(cv, 150, 230)
    flag_pole(cv, 150, 300)
    flag_eu(cv, 150, 300)
    flag_pole(cv, 790, 265)
    flag_usa(cv, 790, 265)
    cv.rect(112, 448, 800, 48, NAVY)
    draw_text(cv, "EUROPE JOINS UKRAINE TALKS", 512, 461, 3, WHITE,
              center=True)

    # six vignettes, 2 rows x 3 columns
    grid = [
        (16, 516, v_nvidia, "NVIDIA CEO RESIGNS"),
        (352, 516, v_microsoft, "MICROSOFT OUTAGE"),
        (688, 516, v_hospital, "HOSPITAL STRIKE KILLS SIX"),
        (16, 756, v_warship, "DRONE HITS RUSSIAN WARSHIP"),
        (352, 756, v_hack, "FBI: N. KOREA $400M HACK"),
        (688, 756, v_kane, "KANE BREAKS ENGLAND RECORD"),
    ]
    for x, y, fn, lab in grid:
        cell(cv, x, y)
        fn(cv, x, y)
        label(cv, x, y, lab)
    return cv


# --------------------------------------------------------------------- png
def png_bytes(cv):
    raw = b"".join(
        b"\x00" + bytes(cv.buf[y * W * 3:(y + 1) * W * 3])
        for y in range(H)
    )

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
