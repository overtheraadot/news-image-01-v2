#!/usr/bin/env python3
"""News-image-01 -- one image summing up Friday 13 November 2026.

A magazine front page drawn with nothing but the Python standard
library (zlib for the PNG encoder). No network, no files read, no
randomness: the same bytes come out on every run.

Layout: a masthead ("13 NOVEMBER 2026" / "THE WORLD TODAY"), a central
globe with a dove and three flags for the lead story (Ukraine peace
talks -- US envoys Witkoff and Kushner met Putin in Moscow, Europe
joins the next round, a large prisoner exchange agreed in principle),
and a 2 x 3 grid of flat pictorial vignettes for the other verified
stories of the day. All labels are set in a tiny 5x7 bitmap font
implemented here, drawn with rectangles so the text stays legible.

Stories (all verified against the day's reporting):
  * Nvidia CEO Jensen Huang resigned; the Senate summoned Huang and
    Lutnick; shares closed down ~4%.
  * Microsoft 365 global outage: Outlook, Teams and Copilot down
    across 74 countries.
  * Israeli strike on Nasser Hospital, Khan Younis, kills six,
    including a surgeon and a 13-year-old.
  * Ukrainian drone hits a Russian warship in the Gulf of Finland.
  * FBI: North Korean hackers stole $400m in crypto via fake
    video calls.
  * Harry Kane breaks England's appearance record (126 caps)
    vs Croatia.
"""

import math
import os
import struct
import zlib

W = H = 1024
OUT_NAME = "entry.png"

# ------------------------------------------------------------------ palette
PAPER = (245, 240, 230)      # warm newsprint
PAPER_DK = (232, 225, 210)
INK = (27, 42, 74)           # deep newsroom navy
INK_SOFT = (58, 68, 96)
RED = (176, 46, 46)          # masthead red / alert red
GOLD = (201, 151, 63)
GOLD_LT = (232, 190, 110)
OCEAN = (46, 110, 166)
OCEAN_DK = (28, 74, 128)
OCEAN_LT = (96, 158, 205)
LAND = (196, 176, 120)
LAND_GREEN = (110, 150, 104)
WHITE = (250, 250, 246)
DOVE = (252, 252, 248)
DOVE_SHADE = (214, 214, 206)
LEAF = (84, 128, 70)
SLATE = (84, 92, 118)
SLATE_DK = (52, 58, 84)
CHIP = (38, 44, 68)
WARN = (240, 176, 40)
HOSP = (52, 104, 116)
SEA = (64, 96, 132)
SEA_DK = (44, 70, 102)
SHIP = (70, 76, 92)
SHIP_DK = (44, 48, 62)
SMOKE = (150, 150, 148)
LAPTOP = (40, 44, 60)
MASK = (236, 236, 230)
GREY_LINE = (196, 188, 172)
MUTE = (120, 114, 100)

# ------------------------------------------------------------------ 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
    "A": (" .###. ", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}
# Normalise: strip the padding spaces I typed on the first row of "A".
FONT = {k: tuple(row.strip()[:5].ljust(5, ".") for row in v)
        for k, v in FONT.items()}


def text_width(s, scale):
    """Pixel width of s at the given scale (1px gap between glyphs)."""
    if not s:
        return 0
    return len(s) * 6 * scale - scale


# ------------------------------------------------------------------ canvas
class Board:
    """Flat RGB buffer with small filled-shape primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, rgb):
        self.px[:] = bytes(rgb) * (self.w * self.h)

    def hline(self, y, x0, x1, rgb):
        if y < 0 or y >= self.h:
            return
        x0 = max(0, int(x0))
        x1 = min(self.w - 1, int(x1))
        if x1 < x0:
            return
        i = (y * self.w + x0) * 3
        self.px[i:i + 3 * (x1 - x0 + 1)] = bytes(rgb) * (x1 - x0 + 1)

    def rect(self, x, y, w, h, rgb):
        for yy in range(int(y), int(y + h)):
            self.hline(yy, x, x + w - 1, rgb)

    def disc(self, cx, cy, r, rgb):
        r = int(r)
        for y in range(max(0, cy - r), min(self.h - 1, cy + r) + 1):
            dy = y - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(y, cx - dx, cx + dx, rgb)

    def ellipse(self, cx, cy, rx, ry, rgb):
        rx, ry = int(rx), int(ry)
        for y in range(max(0, cy - ry), min(self.h - 1, cy + ry) + 1):
            t = (y - cy) / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            self.hline(y, cx - dx, cx + dx, rgb)

    def ring(self, cx, cy, r, thick, rgb):
        for k in range(720):
            th = 2 * math.pi * k / 720
            self.disc(int(cx + r * math.cos(th)),
                      int(cy + r * math.sin(th)), thick, rgb)

    def ellipse_arc(self, cx, cy, rx, ry, rgb, a0=0.0, a1=2 * math.pi):
        steps = 240
        for i in range(steps + 1):
            th = a0 + (a1 - a0) * i / steps
            self.disc(int(cx + rx * math.cos(th)),
                      int(cy + ry * math.sin(th)), 1, rgb)

    def poly(self, pts, rgb):
        """Scanline polygon fill (even-odd pairing)."""
        edges = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if y0 != y1:
                edges.append((y0, y1, x0, x1))
        if not edges:
            return
        ymin = max(0, int(min(p[1] for p in pts)))
        ymax = min(self.h - 1, int(max(p[1] for p in pts)))
        for y in range(ymin, ymax + 1):
            xs = []
            for y0, y1, x0, x1 in edges:
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(y, math.ceil(xs[i]), math.floor(xs[i + 1]), rgb)

    def line(self, x0, y0, x1, y1, rgb, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            self.disc(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t),
                      thick, rgb)

    def bezier(self, p0, p1, p2, rgb, thick=1, steps=24):
        prev = None
        for i in range(steps + 1):
            t = i / steps
            u = 1.0 - t
            x = int(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0])
            y = int(u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])
            if prev is not None:
                self.line(prev[0], prev[1], x, y, rgb, thick)
            prev = (x, y)

    def text(self, x, y, s, scale, rgb, align="left"):
        """Draw s in the 5x7 font; y is the top row. Returns pixel width."""
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT[" "])
            for r, row in enumerate(glyph):
                for c, cell in enumerate(row):
                    if cell == "#":
                        self.rect(cx + c * scale, y + r * scale,
                                  scale, scale, rgb)
            cx += 6 * scale
        return w


# ------------------------------------------------------------------ masthead
def draw_masthead(b):
    b.rect(0, 0, W, 10, RED)
    b.text(W // 2, 30, "13 NOVEMBER 2026", 5, INK, align="center")
    b.text(W // 2, 82, "THE WORLD TODAY", 3, RED, align="center")
    b.rect(48, 122, W - 96, 3, INK)
    b.rect(48, 129, W - 96, 1, INK)


# ------------------------------------------------------------------ the globe
# Rough continent blobs, relative to the globe centre.
CONTINENTS = [
    [(-118, -58), (-92, -88), (-58, -78), (-40, -52), (-52, -28),
     (-84, -18), (-112, -30)],                       # N. America
    [(-52, -88), (-38, -92), (-28, -78), (-44, -72)],  # Greenland
    [(-66, 14), (-44, 4), (-30, 22), (-36, 62), (-52, 78),
     (-68, 52), (-74, 26)],                          # S. America
    [(6, -34), (34, -44), (52, -18), (44, 22), (22, 44),
     (2, 34), (-10, 2)],                             # Africa
    [(34, -72), (76, -88), (112, -70), (118, -30), (92, -14),
     (60, -34), (40, -52)],                          # Eurasia
    [(72, 46), (102, 42), (112, 62), (88, 74), (70, 62)],  # Australia
]

GX, GY, GR = 512, 312, 140


def draw_globe(b):
    b.disc(GX, GY, GR, OCEAN)
    # light from the upper left, dusk shade lower right
    b.ellipse(GX - 46, GY - 52, 62, 44, OCEAN_LT)
    b.ellipse(GX + 58, GY + 56, 66, 48, OCEAN_DK)
    for pts in CONTINENTS:
        b.poly([(GX + int(x * 1.1), GY + int(y * 1.1)) for x, y in pts],
               LAND)
    b.ellipse(GX + 28, GY + 6, 14, 9, LAND_GREEN)
    b.ellipse(GX + 84, GY - 58, 18, 8, LAND_GREEN)
    # latitude / longitude lines
    b.ellipse_arc(GX, GY, GR - 2, 44, OCEAN_DK)
    b.ellipse_arc(GX, GY, GR - 2, 88, OCEAN_DK)
    b.ellipse_arc(GX, GY, 44, GR - 2, OCEAN_DK)
    b.ellipse_arc(GX, GY, 88, GR - 2, OCEAN_DK)
    b.ring(GX, GY, GR, 3, GOLD)
    b.ring(GX, GY, GR + 7, 1, GOLD)


def draw_dove(b):
    # White dove rising beside the globe's upper right, olive branch
    # in its beak. The wing is drawn wide and rooted in the body so it
    # reads as one bird, not a detached sail.
    # Tail feathers fanning to the left.
    b.poly([(636, 212), (596, 192), (588, 206), (632, 226)], DOVE_SHADE)
    b.poly([(640, 222), (606, 212), (600, 224), (638, 232)], DOVE_SHADE)
    # Raised wing sweeping up, base overlapping the body.
    b.poly([(644, 214), (618, 140), (592, 150), (622, 200), (648, 222)],
           DOVE)
    b.poly([(644, 214), (628, 162), (612, 164), (634, 206)], DOVE_SHADE)
    # Body: long ellipse tilted up to the right.
    b.ellipse(700, 212, 58, 24, DOVE)
    # Head, eye, beak.
    b.disc(756, 192, 15, DOVE)
    b.poly([(768, 186), (786, 192), (768, 198)], GOLD)
    b.disc(760, 188, 3, INK)
    # Olive branch trailing from the beak.
    b.bezier((784, 194), (812, 202), (830, 226), LEAF, thick=2)
    for lx, ly in [(800, 200), (812, 212), (822, 222)]:
        b.ellipse(lx, ly, 10, 4, LEAF)
    # A few drifting feathers below.
    for x, y, r in [(660, 254, 4), (692, 264, 3), (724, 256, 4)]:
        b.disc(x, y, r, DOVE_SHADE)


def draw_flags(b):
    """Three small flags under the globe: Ukraine, EU, USA."""
    y = 456
    # Ukraine: blue over yellow.
    b.rect(443, y, 36, 7, (0, 87, 183))
    b.rect(443, y + 7, 36, 7, (255, 215, 0))
    # EU: blue field, ring of gold stars.
    b.rect(494, y, 36, 14, (0, 51, 153))
    for k in range(8):
        th = 2 * math.pi * k / 8
        b.disc(int(512 + 5 * math.cos(th)), int(y + 7 + 5 * math.sin(th)),
               1, GOLD_LT)
    # USA: stripes + canton.
    for i in range(7):
        b.rect(545, y + i * 2, 36, 2, RED if i % 2 == 0 else WHITE)
    b.rect(545, y, 15, 8, (0, 40, 104))
    b.disc(552, y + 4, 1, WHITE)
    # Thin poles.
    for fx in (441, 492, 543):
        b.line(fx, y - 4, fx, y + 14, INK_SOFT, 1)


def draw_lead_banner(b):
    b.rect(140, 478, W - 280, 32, INK)
    b.text(W // 2, 485, "EUROPE JOINS UKRAINE TALKS", 3, WHITE,
           align="center")
    b.rect(140, 514, W - 280, 2, GOLD)


# ------------------------------------------------------------------ vignettes
# Grid: 3 columns (centres 171 / 512 / 853), 2 rows (tops 528 / 768).
# Each cell: picture zone ~160px tall, one label line underneath.
CELL_CX = (171, 512, 853)
CELL_TOP = (528, 768)


def vignette_frame(b, cx, top):
    b.rect(cx - 150, top, 300, 160, PAPER_DK)
    b.rect(cx - 150, top + 160, 300, 2, GOLD)


def vignette_label(b, cx, top, label):
    b.text(cx, top + 176, label, 2, INK, align="center")


def draw_chair_chip(b, cx, top):
    """Vignette 1 -- Nvidia: an empty witness chair, a chip, a red fall."""
    vignette_frame(b, cx, top)
    # Empty chair (navy), seat facing right.
    b.rect(cx - 78, top + 22, 12, 66, INK)            # backrest
    b.rect(cx - 78, top + 22, 46, 10, INK)            # backrest top
    b.rect(cx - 78, top + 84, 118, 12, INK)           # seat
    b.rect(cx - 70, top + 96, 8, 30, INK)             # legs
    b.rect(cx + 30, top + 96, 8, 30, INK)
    # Chip on the seat, gold core, pins on both sides.
    b.rect(cx + 8, top + 26, 58, 58, CHIP)
    b.rect(cx + 20, top + 38, 34, 34, GOLD)
    b.rect(cx + 30, top + 48, 14, 14, CHIP)
    for py in (top + 34, top + 48, top + 62):
        b.rect(cx + 0, py, 8, 5, GOLD)
        b.rect(cx + 66, py, 8, 5, GOLD)
    # Red down arrow at the right: the share price fell.
    b.rect(cx + 104, top + 30, 10, 44, RED)
    b.poly([(cx + 96, top + 72), (cx + 122, top + 72), (cx + 109, top + 96)],
           RED)
    vignette_label(b, cx, top, "NVIDIA CEO RESIGNS")


def draw_envelope(b, cx, top):
    """Vignette 2 -- Microsoft outage: dark envelope, warning triangle."""
    vignette_frame(b, cx, top)
    b.rect(cx - 72, top + 30, 144, 74, SLATE)
    b.poly([(cx - 72, top + 30), (cx, top + 74), (cx + 72, top + 30)],
           SLATE_DK)
    b.poly([(cx - 72, top + 104), (cx - 30, top + 66), (cx + 30, top + 66),
            (cx + 72, top + 104)], SLATE_DK)
    # Warning triangle overlapping the lower right corner.
    b.poly([(cx + 34, top + 112), (cx + 62, top + 58), (cx + 90, top + 112)],
           WARN)
    b.poly([(cx + 42, top + 104), (cx + 62, top + 68), (cx + 82, top + 104)],
           (176, 108, 20))
    b.rect(cx + 59, top + 78, 6, 16, WARN)
    b.disc(cx + 62, top + 100, 3, WARN)
    vignette_label(b, cx, top, "MICROSOFT OUTAGE")


def draw_hospital(b, cx, top):
    """Vignette 3 -- Khan Younis: hospital block with cross, candle."""
    vignette_frame(b, cx, top)
    b.rect(cx - 82, top + 34, 118, 92, HOSP)
    b.rect(cx - 82, top + 34, 118, 8, (38, 78, 88))
    # White cross on the facade.
    b.rect(cx - 40, top + 48, 16, 44, WHITE)
    b.rect(cx - 52, top + 60, 40, 16, WHITE)
    # Dark windows.
    for wx in (cx - 74, cx + 2):
        for wy in (top + 48, top + 76):
            b.rect(wx, wy, 18, 14, INK)
    # Candle at the right, flame above.
    b.rect(cx + 56, top + 82, 18, 44, (240, 232, 210))
    b.rect(cx + 63, top + 74, 4, 8, INK)
    b.poly([(cx + 65, top + 44), (cx + 75, top + 66), (cx + 55, top + 66)],
           (244, 150, 52))
    b.poly([(cx + 65, top + 54), (cx + 71, top + 66), (cx + 59, top + 66)],
           (255, 214, 110))
    vignette_label(b, cx, top, "HOSPITAL STRIKE KILLS SIX")


def draw_warship(b, cx, top):
    """Vignette 4 -- Gulf of Finland: warship on a grey sea, smoke."""
    vignette_frame(b, cx, top)
    # Grey sea with two wave lines.
    b.rect(cx - 150, top + 96, 300, 36, SEA)
    b.bezier((cx - 140, top + 108), (cx - 70, top + 100),
             (cx, top + 108), SEA_DK, thick=2)
    b.bezier((cx, top + 108), (cx + 70, top + 100),
             (cx + 140, top + 108), SEA_DK, thick=2)
    b.bezier((cx - 140, top + 122), (cx - 70, top + 114),
             (cx, top + 122), SEA_DK, thick=2)
    b.bezier((cx, top + 122), (cx + 70, top + 114),
             (cx + 140, top + 122), SEA_DK, thick=2)
    # Hull and superstructure.
    b.poly([(cx - 88, top + 66), (cx + 88, top + 66), (cx + 70, top + 98),
            (cx - 70, top + 98)], SHIP)
    b.rect(cx - 88, top + 66, 176, 6, SHIP_DK)
    b.rect(cx - 40, top + 34, 64, 32, SHIP_DK)
    b.rect(cx - 18, top + 18, 20, 16, SHIP_DK)
    b.line(cx - 8, top + 18, cx - 8, top + 2, SHIP_DK, 2)
    # Smoke plume from the funnel, drifting right.
    for sx, sy, r in [(cx + 8, top + 12, 9), (cx + 26, top + 2, 12),
                      (cx + 48, top - 6, 10)]:
        b.disc(sx, sy, r, SMOKE)
    vignette_label(b, cx, top, "DRONE HITS RUSSIAN WARSHIP")


def draw_laptop(b, cx, top):
    """Vignette 5 -- FBI hack: laptop with a masked face, gold coins."""
    vignette_frame(b, cx, top)
    # Laptop screen and base.
    b.rect(cx - 74, top + 22, 148, 84, LAPTOP)
    b.rect(cx - 62, top + 32, 124, 64, (16, 20, 36))
    b.rect(cx - 88, top + 106, 176, 12, SLATE_DK)
    # Masked face on the screen: pale oval, dark eye slits, hood line.
    b.ellipse(cx, top + 62, 26, 30, MASK)
    b.ellipse(cx, top + 34, 26, 12, LAPTOP)
    b.rect(cx - 16, top + 52, 12, 5, INK)
    b.rect(cx + 4, top + 52, 12, 5, INK)
    b.rect(cx - 4, top + 78, 8, 3, INK)
    # Gold coins spilling at the right.
    for ox, oy, r in [(cx + 92, top + 96, 17), (cx + 116, top + 108, 14),
                      (cx + 70, top + 112, 12)]:
        b.disc(ox, oy, r, GOLD)
        b.ring(ox, oy, r - 5, 1, GOLD_LT)
    b.text(cx + 92, top + 88, "$", 2, INK, align="center")
    vignette_label(b, cx, top, "FBI: N. KOREA $400M HACK")


def draw_footballer(b, cx, top):
    """Vignette 6 -- Kane: England footballer in white, ball at his boot."""
    vignette_frame(b, cx, top)
    # Simple footballer: head, white shirt, navy shorts, legs, one boot
    # swung toward the ball.
    b.disc(cx - 28, top + 28, 12, (198, 150, 110))        # head
    b.ellipse(cx - 28, top + 20, 12, 6, (60, 44, 30))     # hair
    b.rect(cx - 42, top + 44, 30, 40, WHITE)              # shirt
    b.rect(cx - 42, top + 44, 30, 40, INK)                # (border pass)
    b.rect(cx - 40, top + 46, 26, 36, WHITE)              # shirt fill
    b.rect(cx - 40, top + 84, 26, 14, INK_SOFT)           # shorts
    b.rect(cx - 38, top + 98, 9, 26, (198, 150, 110))     # standing leg
    b.line(cx - 22, top + 100, cx + 22, top + 118, (198, 150, 110),
           thick=4)                                       # kicking leg
    b.line(cx - 48, top + 52, cx - 62, top + 74, WHITE, thick=4)  # arm
    b.line(cx - 12, top + 52, cx + 6, top + 66, WHITE, thick=4)   # arm
    # Ball at the boot, with pentagon marks.
    b.disc(cx + 44, top + 112, 18, WHITE)
    b.ring(cx + 44, top + 112, 18, 1, INK)
    b.disc(cx + 44, top + 112, 5, INK)
    for k in range(5):
        th = -math.pi / 2 + 2 * math.pi * k / 5
        b.disc(int(cx + 44 + 13 * math.cos(th)),
               int(top + 112 + 13 * math.sin(th)), 2, INK)
    # Motion ticks behind the ball.
    for mx in (cx + 66, cx + 74):
        b.line(mx, top + 104, mx + 8, top + 104, GOLD, thick=2)
        b.line(mx, top + 114, mx + 8, top + 114, GOLD, thick=2)
    vignette_label(b, cx, top, "KANE BREAKS ENGLAND RECORD")


# ------------------------------------------------------------------ PNG out
def encode_png(b):
    raw = bytearray()
    for y in range(b.h):
        raw.append(0)  # filter: none
        raw += b.px[y * b.w * 3:(y + 1) * b.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", b.w, b.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------------ compose
def compose():
    b = Board(W, H, PAPER)
    draw_masthead(b)
    draw_globe(b)
    draw_dove(b)
    draw_flags(b)
    draw_lead_banner(b)
    # Grid rules.
    b.rect(0, CELL_TOP[1] - 6, W, 1, GREY_LINE)
    b.rect(341, CELL_TOP[0], 1, 432, GREY_LINE)
    b.rect(682, CELL_TOP[0], 1, 432, GREY_LINE)
    draw_chair_chip(b, CELL_CX[0], CELL_TOP[0])
    draw_envelope(b, CELL_CX[1], CELL_TOP[0])
    draw_hospital(b, CELL_CX[2], CELL_TOP[0])
    draw_warship(b, CELL_CX[0], CELL_TOP[1])
    draw_laptop(b, CELL_CX[1], CELL_TOP[1])
    draw_footballer(b, CELL_CX[2], CELL_TOP[1])
    b.text(W // 2, 992, "MAKE.FUN - NEWS-IMAGE-01", 1, MUTE,
           align="center")
    return b


def main():
    board = compose()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, OUT_NAME)
    data = encode_png(board)
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
