# news-image-20261125 — "The World Today": Wednesday 25 November 2026 in one image.
#
# A single 1024x1024 PNG drawn from scratch in pure Python 3.13 (standard
# library only) and written to /output/entry.png. No network, no clock, no
# randomness: running it twice produces byte-identical output.
#
# Six stories from what the wire services reported on 25 November 2026:
# Zelenskyy confirming Ukraine's Gulf of Finland ship strike, the Houthi
# drone hit on Riyadh's tallest tower, Huawei's conviction in the US trial
# over its Iran business, NATO's vow to defend space, the Sarkozy case
# going to trial, and Iran's mined tankers in the Strait of Hormuz.
# The footer ticker carries six more briefs from the same day.
#
# Run:  python3 main.py        (writes /output/entry.png, or $MAKEFUN_OUTPUT_DIR)

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---- palette: a dark "evening edition" — ink navy page, paper panels ----
INK_NAVY = (13, 27, 48)
DEEP_BLUE = (18, 42, 74)
PAPER = (250, 246, 236)
CARD = (255, 255, 255)
CARD_SHADE = (233, 228, 214)
INK = (18, 18, 18)
GREY = (88, 88, 88)
GOLD = (212, 164, 32)
CREAM = (255, 244, 214)
WHITE = (255, 255, 255)
SEA = (24, 68, 110)
SEA_LIGHT = (52, 116, 168)
SKY = (196, 220, 238)
RED = (178, 34, 34)
TEAL = (13, 110, 102)
PURPLE = (88, 60, 140)
RUST = (176, 92, 32)
GREEN = (58, 110, 58)


class Canvas:
    """A flat RGB buffer with tiny shape helpers, origin top-left."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            for _ in range(x1 - x0):
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c
                i += 3

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, half * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c):
        steps = max(28, r * 6)
        for s in range(steps):
            a = s / steps * 6.283185307179586
            self.dot(round(cx + r * __import__("math").cos(a)),
                     round(cy + r * __import__("math").sin(a)), c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        while True:
            self.dot(x, y, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        """Scanline-filled polygon from a list of (x, y) corners."""
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h - 1, max(ys)) + 1):
            hits = []
            for i, (ax, ay) in enumerate(pts):
                bx, by = pts[(i + 1) % len(pts)]
                if (ay <= y < by) or (by <= y < ay):
                    hits.append(ax + (y - ay) / (by - ay) * (bx - ax))
            hits.sort()
            for k in range(0, len(hits) - 1, 2):
                self.rect(round(hits[k]), y, round(hits[k + 1]) - round(hits[k]), 1, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)


def _crc(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", _crc(tag + data)))


def to_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b""))


# ---- 5x7 bitmap type: each glyph is 7 rows, each row a 5-bit integer ----
# Bit 4 is the leftmost column. Only capitals are drawn; text is uppercased.
GLYPHS = {
    "A": [0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "B": [0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E],
    "C": [0x0F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0F],
    "D": [0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E],
    "E": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F],
    "F": [0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10],
    "G": [0x0F, 0x10, 0x10, 0x17, 0x11, 0x11, 0x0F],
    "H": [0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11],
    "I": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1F],
    "J": [0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C],
    "K": [0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11],
    "L": [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F],
    "M": [0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11],
    "N": [0x11, 0x19, 0x19, 0x15, 0x13, 0x13, 0x11],
    "O": [0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "P": [0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10],
    "Q": [0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D],
    "R": [0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11],
    "S": [0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E],
    "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],
    "U": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E],
    "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04],
    "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],
    "X": [0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11],
    "Y": [0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04],
    "Z": [0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F],
    "0": [0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E],
    "1": [0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E],
    "2": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F],
    "3": [0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E],
    "4": [0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02],
    "5": [0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E],
    "6": [0x0E, 0x10, 0x10, 0x1E, 0x11, 0x11, 0x0E],
    "7": [0x1F, 0x01, 0x02, 0x04, 0x04, 0x04, 0x04],
    "8": [0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E],
    "9": [0x0E, 0x11, 0x11, 0x0F, 0x01, 0x01, 0x0E],
    " ": [0, 0, 0, 0, 0, 0, 0],
    ".": [0, 0, 0, 0, 0, 0x0C, 0x0C],
    ",": [0, 0, 0, 0, 0x0C, 0x0C, 0x04],
    ":": [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0],
    ";": [0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0x04],
    "'": [0x04, 0x04, 0x04, 0, 0, 0, 0],
    "-": [0, 0, 0, 0x1F, 0, 0, 0],
    "/": [0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10],
    "(": [0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02],
    ")": [0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08],
    "&": [0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D],
    "%": [0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13],
    "!": [0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04],
    "?": [0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04],
    "+": [0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0],
    "=": [0, 0, 0x1F, 0, 0x1F, 0, 0],
    '"': [0x0A, 0x0A, 0x0A, 0, 0, 0, 0],
    "$": [0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04],
    "•": [0, 0, 0x0E, 0x1F, 0x1F, 0x0E, 0],
}
CW, CH = 5, 7  # glyph cell size in units


def glyph_w(scale):
    return (CW + 1) * scale


def text_w(s, scale):
    return max(0, len(s) * glyph_w(scale) - scale)


def draw_text(cv, s, x, y, scale, colour):
    cx = x
    for ch in s.upper():
        rows = GLYPHS.get(ch, GLYPHS["?"])
        for r, bits in enumerate(rows):
            for col in range(CW):
                if bits & (1 << (CW - 1 - col)):
                    cv.rect(cx + col * scale, y + r * scale, scale, scale, colour)
        cx += glyph_w(scale)
    return cx


def draw_centred(cv, s, cx, y, scale, colour):
    draw_text(cv, s, cx - text_w(s, scale) // 2, y, scale, colour)


def wrap(s, scale, max_w):
    lines, cur = [], ""
    for word in s.upper().split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, s, x, y, scale, max_w, colour, gap=3):
    """Draw wrapped text; returns the number of lines drawn."""
    lines = wrap(s, scale, max_w)
    for i, ln in enumerate(lines):
        draw_text(cv, ln, x, y + i * (CH * scale + gap), scale, colour)
    return len(lines)


# ---- picture scenes: each draws inside the (x, y, w, h) band it is given ----

def scene_sea(cv, x, y, w, h):
    """Gulf of Finland: a cargo ship on dark water, a drone above it."""
    cv.rect(x, y, w, h, SEA)
    cv.rect(x, y, w, h // 3, (28, 52, 84))
    cv.disc(x + w - 52, y + 30, 13, CREAM)  # low moon
    for k in range(4):  # wave lines
        yy = y + h // 2 + 8 + k * 14
        for xx in range(x + 8, x + w - 8, 26):
            cv.rect(xx, yy, 14, 3, SEA_LIGHT)
    cx, cy = x + w // 2, y + h // 2 + 6
    cv.poly([(cx - 118, cy), (cx + 118, cy), (cx + 96, cy + 30), (cx - 96, cy + 30)],
            (52, 56, 60))  # hull
    cv.rect(cx - 96, cy - 26, 60, 26, RUST)   # containers
    cv.rect(cx - 30, cy - 26, 44, 26, GOLD)
    cv.rect(cx + 20, cy - 26, 52, 26, TEAL)
    cv.rect(cx - 8, cy - 46, 30, 20, CARD)    # bridge
    cv.rect(cx + 96, cy - 40, 4, 40, INK)     # mast
    cv.disc(cx + 118, cy - 34, 4, RED)        # drone light
    dx, dy = x + w - 90, y + 26
    cv.rect(dx - 16, dy - 3, 32, 6, INK)      # drone body
    cv.rect(dx - 24, dy - 8, 10, 3, INK)
    cv.rect(dx + 14, dy - 8, 10, 3, INK)
    cv.line(dx, dy + 4, dx - 30, dy + 34, GOLD)
    cv.line(dx - 30, dy + 34, dx - 52, dy + 52, GOLD)


def scene_tower(cv, x, y, w, h):
    """Riyadh: the PIF Tower with an impact flash near its crown."""
    cv.rect(x, y, w, h, (24, 32, 52))
    for k in range(14):  # city lights
        cv.rect(x + 10 + (k * 37) % (w - 20), y + h - 14 - (k * 5) % 12, 4, 4, GOLD)
    cx = x + w // 2
    top = y + 8
    cv.rect(cx - 26, top + 14, 52, h - 22, (96, 116, 148))  # tower shaft
    cv.poly([(cx - 26, top + 14), (cx + 26, top + 14), (cx, top)], (140, 160, 190))
    for k in range(2):  # lit windows
        cv.rect(cx - 20, top + 22 + k * 12, 40, 4, (220, 200, 120))
    bx, by = cx + 4, top + 10
    for k in range(8):  # impact burst
        a = k * 0.785398
        cv.line(bx, by, round(bx + 18 * __import__("math").cos(a)),
                round(by + 18 * __import__("math").sin(a)), GOLD)
    cv.disc(bx, by, 7, (255, 220, 90))
    cv.disc(bx, by, 3, RED)


def scene_court(cv, x, y, w, h):
    """Washington courtroom: columns, pediment, and a chip on the docket."""
    cv.rect(x, y, w, h, (38, 46, 66))
    cx = x + w // 2
    cv.poly([(cx - 52, y + 16), (cx + 52, y + 16), (cx, y + 4)], CARD_SHADE)
    for k in range(3):
        px = cx - 40 + k * 34
        cv.rect(px, y + 18, 10, h - 26, CARD)
    cv.rect(cx - 18, y + h - 14, 36, 10, INK)  # chip
    cv.rect(cx - 11, y + h - 11, 22, 4, (52, 52, 52))


def scene_satellite(cv, x, y, w, h):
    """Orbit: Earth rising from below, a satellite crossing a ringed sky."""
    cv.rect(x, y, w, h, (10, 16, 36))
    for k in range(18):  # stars
        cv.dot(x + 8 + (k * 53) % (w - 16), y + 5 + (k * 17) % (h // 2), WHITE)
    cx = x + w // 2
    cy = y + h - 16  # Earth disc fully inside the band: cap at its bottom
    cv.disc(cx, cy, 16, SEA)
    cv.disc(cx - 6, cy - 5, 5, GREEN)
    cv.disc(cx + 6, cy + 3, 4, GREEN)
    sx, sy = cx - 8, y + 14
    cv.rect(sx - 26, sy - 3, 16, 6, GOLD)   # solar panels
    cv.rect(sx + 16, sy - 3, 16, 6, GOLD)
    cv.rect(sx - 4, sy - 6, 16, 12, CARD)   # body
    cv.disc(sx + 18, sy, 3, RED)           # dish
    cv.line(sx - 30, sy + 14, sx + 44, sy - 10, (120, 140, 180))  # orbit path


def scene_gavel(cv, x, y, w, h):
    """Paris court: a gavel striking its block."""
    cv.rect(x, y, w, h, (64, 44, 66))
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.poly([(cx - 34, cy - 12), (cx - 8, cy - 20), (cx, cy - 8),
             (cx - 26, cy)], (150, 110, 60))  # gavel head
    cv.line(cx - 22, cy - 12, cx + 22, cy + 10, (110, 76, 40))  # handle
    cv.line(cx - 20, cy - 8, cx + 24, cy + 14, (110, 76, 40))
    cv.rect(cx - 36, cy + 12, 72, 6, (90, 70, 44))  # sound block
    for k in range(3):  # motion ticks
        cv.rect(cx + 30 + k * 6, cy - 18 + k * 7, 3, 8, GOLD)


def scene_tanker(cv, x, y, w, h):
    """Strait of Hormuz: a tanker passing a spiked mine."""
    cv.rect(x, y, w, h, (16, 44, 60))
    for k in range(2):
        yy = y + h - 16 + k * 7
        for xx in range(x + 6, x + w - 6, 24):
            cv.rect(xx, yy, 12, 3, SEA_LIGHT)
    cx, cy = x + w // 2 - 16, y + h // 2 + 6
    cv.poly([(cx - 76, cy), (cx + 76, cy), (cx + 60, cy + 14), (cx - 60, cy + 14)],
            (120, 40, 36))  # tanker hull
    cv.rect(cx - 60, cy - 12, 108, 12, (200, 200, 200))
    cv.rect(cx + 54, cy - 20, 18, 20, CARD)
    mx, my = x + w - 40, y + h // 2 - 2
    cv.disc(mx, my, 8, INK)  # mine
    for k in range(8):
        a = k * 0.785398
        cv.line(mx, my, round(mx + 13 * __import__("math").cos(a)),
                round(my + 13 * __import__("math").sin(a)), INK)
    cv.disc(mx, my, 3, RED)


SCENES = {
    "sea": scene_sea, "tower": scene_tower, "court": scene_court,
    "sat": scene_satellite, "gavel": scene_gavel, "tanker": scene_tanker,
}


def card(cv, x, y, w, h, accent, kicker, headline, body, scene, scene_h):
    """One story panel: accent kicker bar, picture band, headline, body."""
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK)
    cv.rect(x + 2, y + 2, w - 4, 30, accent)
    draw_text(cv, kicker, x + 12, y + 11, 2, WHITE)
    SCENES[scene](cv, x + 2, y + 32, w - 4, scene_h)
    tx, tw = x + 12, w - 24
    hy = y + 32 + scene_h + 10
    n = draw_block(cv, headline, tx, hy, 3, tw, INK, 4)
    draw_block(cv, body, tx, hy + n * 25 + 8, 2, tw, GREY, 3)


# ---- the page ----

def build_page():
    cv = Canvas(W, H, INK_NAVY)

    # Masthead: kicker, title, gold dateline bar.
    draw_centred(cv, "ONE DAY IN ONE PICTURE", W // 2, 22, 2, GOLD)
    draw_centred(cv, "THE WORLD TODAY", W // 2, 48, 6, PAPER)
    cv.rect(24, 106, W - 48, 30, GOLD)
    draw_centred(cv, "WEDNESDAY 25 NOVEMBER 2026", W // 2, 113, 3, INK_NAVY)
    cv.rect(24, 144, W - 48, 2, GOLD)

    # Lead story: picture on the left, words on the right.
    hx, hy, hw, hh = 24, 152, W - 48, 292
    cv.rect(hx, hy, hw, hh, CARD)
    cv.frame(hx, hy, hw, hh, INK)
    cv.rect(hx + 2, hy + 2, hw - 4, 30, SEA)
    draw_text(cv, "GULF OF FINLAND - UKRAINE", hx + 12, hy + 11, 2, WHITE)
    draw_text(cv, "LEAD STORY", hx + hw - 12 - text_w("LEAD STORY", 2), hy + 11, 2, GOLD)
    scene_sea(cv, hx + 2, hy + 32, 330, hh - 34)
    tx = hx + 330 + 18
    tw = hx + hw - 14 - tx
    n = draw_block(cv, "ZELENSKYY CONFIRMS UKRAINE STRUCK RUSSIAN SHIP",
                   tx, hy + 52, 4, tw, INK, 5)
    draw_block(cv,
               "KYIV SAYS ITS DRONES HIT A RUSSIAN CARGO SHIP IN THE GULF OF "
               "FINLAND ON SATURDAY. ALLY NORWAY URGES CAUTION AS THE WAR AT "
               "SEA WIDENS.",
               tx, hy + 52 + n * 33 + 12, 2, tw, GREY, 4)

    # Middle row: Riyadh and Huawei.
    my, mh, mw = 460, 252, 480
    card(cv, 24, my, mw, mh, RED, "RIYADH - YEMEN",
         "HOUTHIS HIT RIYADH'S TALLEST TOWER",
         "AT LEAST 11 WOUNDED AS A DRONE STRIKES THE PIF TOWER, THE SECOND "
         "HIT ON THE CAPITAL IN UNDER A WEEK.",
         "tower", 56)
    card(cv, 520, my, mw, mh, PURPLE, "USA - CHINA",
         "HUAWEI CONVICTED IN US TRIAL OVER IRAN DEALS",
         "A US JURY FINDS THE CHINESE GIANT GUILTY IN A SPRAWLING CRIMINAL "
         "CASE OVER BUSINESS WITH IRAN.",
         "court", 56)

    # Bottom row: space, Paris, Hormuz.
    by, bh = 728, 214
    card(cv, 24, by, 314, bh, TEAL, "SPACE - NATO",
         "NATO VOWS TO DEFEND SPACE",
         "ALLIES WARN OVER REPORTS RUSSIA MAY LAUNCH A NUCLEAR-ARMED "
         "SATELLITE AS SOON AS DECEMBER.",
         "sat", 44)
    card(cv, 354, by, 314, bh, RUST, "FRANCE",
         "SARKOZY CASE ORDERED TO TRIAL",
         "THE EX-PRESIDENT AND WIFE CARLA BRUNI FACE A CORRUPTION TRIAL. "
         "FIRST HEARING: APRIL 2027.",
         "gavel", 44)
    card(cv, 684, by, 316, bh, SEA, "STRAIT OF HORMUZ - IRAN",
         "TANKERS HIT BY MINES, IRAN SAYS",
         "THREE TANKERS STRUCK IN THE STRAIT AS IRAN BRACES FOR WINTER GAS "
         "SHORTAGES.",
         "tanker", 44)

    # Footer ticker: six more briefs from the same day.
    cv.rect(24, 954, W - 48, 2, GOLD)
    draw_block(cv,
               "ALSO TODAY: EU SANCTIONS RUSSIA - 700,000 RUSSIAN WAR DEAD - "
               "GIULIANI MEDAL OF FREEDOM - KOREA MINISTER QUITS - ENGLAND "
               "WIN T20 - MYANMAR CONDEMNED.",
               24, 966, 2, W - 48, CREAM, 3)
    return cv


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    png = to_png(build_page())
    (out_dir / "entry.png").write_bytes(png)


if __name__ == "__main__":
    main()
