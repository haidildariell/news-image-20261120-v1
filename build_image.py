#!/usr/bin/env python3
"""Render the Friday 20 November 2026 front page as a single 1024x1024 PNG.

Written from scratch in this session from the story brief. Pillow only,
no network, deterministic output (no timestamps, no randomness).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

CREAM = (247, 241, 227)
PAPER = (255, 252, 244)
NAVY = (16, 32, 64)
NAVY2 = (28, 52, 96)
GOLD = (176, 141, 58)
GOLD_LT = (212, 175, 90)
RED = (178, 34, 34)
INK = (22, 22, 22)
GREY = (96, 92, 84)
TEAL = (0, 112, 112)
SKY = (18, 44, 78)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_lines(d, x, y, lines, font, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def centre(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- data
STATS = [
    ("370,000+", "evacuated ahead of Cyclone Akvan"),
    ("3", "Dnipro bridges hit in Kyiv barrage"),
    ("-7%", "Asia shares' worst week since 2020"),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed"),
    ("118", "Phillips' historic century vs India"),
    ("60.7%", "tumours shrank on daraxonrasib + chemo"),
]

REGION = ("ASIA-PACIFIC 11  \u00b7  EUROPE 9  \u00b7  MIDDLE EAST 4  \u00b7  "
          "AMERICAS 13  \u00b7  AFRICA 4  \u00b7  OCEANIA 3  \u00b7  GLOBAL 2  =  46")

LEADS = [
    dict(n=1, place="ODISHA, INDIA", topic="STORM",
         head="Cyclone Akvan makes landfall in eastern India",
         body=("Severe storm crosses near Gopalpur Friday morning; 370,000 "
               "evacuated, 423 rescue teams, winds 70-80 gusting 90 km/h; "
               "no major damage reported."),
         src="Hindu BusinessLine, IMD"),
    dict(n=2, place="KYIV, UKRAINE", topic="WAR",
         head="Russia fires overnight ballistic-missile barrage at Kyiv",
         body=("3 killed, 3 bridges across the Dnipro damaged, fires in "
               "three districts."),
         src="Reuters, livefromeurope"),
    dict(n=3, place="ANTALYA, T\u00dcRKIYE", topic="CLIMATE",
         head="COP31 reaches final day deadlocked",
         body=("Closing draft omits fossil-fuel phase-out and the $120bn "
               "adaptation target; Panama vows to block; \u201c35 by 35\u201d "
               "clean-power goal stays."),
         src="Reuters, AP"),
]

MIDS = [
    dict(n=4, place="SEOUL/TOKYO", topic="MARKETS", colour=(122, 20, 20),
         head="AI sell-off sinks Asia to worst week since 2020",
         body=("Nikkei -4.5%, Kospi -4.7%, Taiex -6.4%; SoftBank -14.6%; "
               "MSCI Asia-Pacific -7% on the week."),
         src="Reuters", icon="chart"),
    dict(n=5, place="MERCURY", topic="SPACE", colour=(28, 52, 96),
         head="BepiColombo reaches Mercury after 8 years",
         body=("ESA/JAXA probe ends 6bn-mile trip; orbit insertion set "
               "for Saturday."),
         src="Guardian, ESA", icon="planet"),
    dict(n=6, place="BRUSSELS", topic="EUROPE", colour=(24, 64, 110),
         head="Burnham holds second EU-UK reset summit",
         body=("Costa & von der Leyen host UK PM; deals on food, emissions "
               "trading, youth mobility for 100,000."),
         src="AP, Le Monde", icon="flags"),
    dict(n=7, place="TOKYO", topic="ECONOMY", colour=(0, 96, 96),
         head="Japan inflation hits 2.3%; BoJ hike eyed",
         body=("Oct headline CPI rises from 2.1%; core 2.2%, above 2% "
               "target for second month."),
         src="Statistics Bureau of Japan, FXStreet", icon="bars"),
    dict(n=8, place="BEIJING", topic="RATES", colour=(96, 64, 16),
         head="China holds lending rates for 18th month",
         body="1-yr LPR 3.00%, 5-yr 3.50% as expected.",
         src="Reuters, PBoC", icon="pct"),
    dict(n=9, place="WELLINGTON", topic="CRICKET", colour=(24, 96, 44),
         head="Phillips makes history with 118 vs India",
         body=("First batter with centuries vs India in all 3 formats in "
               "one calendar year; NZ 368, Nicholls 175*."),
         src="Reuters, ICC", icon="ball"),
    dict(n=10, place="ROME", topic="LABOUR", colour=(150, 60, 10),
         head="Italy's CGIL holds 24-hr general strike",
         body=("Unions rally across ~100 squares against the 2027 budget; "
               "transit hit."),
         src="ANSA, UNI Europa", icon="mega"),
    dict(n=11, place="BARCELONA", topic="HEALTH", colour=(120, 24, 84),
         head="Daraxonrasib + chemo shrinks tumours in 60.7%",
         body=("Early trial, 61 patients, presented Friday at ENA; no "
               "chemo-only comparison yet."),
         src="EORTC, PA", icon="pill"),
    dict(n=12, place="MATO GROSSO, BRAZIL", topic="LAND", colour=(60, 90, 24),
         head="Lula visits ailing Chief Raoni, 94",
         body=("Recognises Kayapo and Yudja ancestral lands "
               "(Kapot Nhinore)."),
         src="One Turn, World Times Daily", icon="leaf"),
]

ONELINERS = [
    (13, "SEOUL", "Ruling party moves to impeach Chief Justice Cho Hee-dae.", "SBS"),
    (14, "BOUGAINVILLE", "Rio Tinto pledges $370m for Panguna mine repair.", "ABC, Reuters"),
    (15, "CANBERRA", "CBO warns AUKUS sub sales could shrink the US fleet.", "Reuters"),
    (16, "FLORIDA", "St Johns River hits record 18.3 ft; four counties shut schools.", "AP"),
    (17, "IOWA", "US Army sets noon detonation of 68 unstable explosive barrels.", "AP"),
    (18, "TONGA", "El Ni\u00f1o drought bites.", "RNZ"),
    (19, "COPENHAGEN", "Denmark's parliament approves Greenland defence bill.", "AFP"),
    (20, "GLOBAL", "UN marks World Children's Day across member states.", "UN News"),
    (21, "DAKAR", "President Faye enacts supplementary budget by decree.", "AFP"),
    (22, "HORMUZ", "Attacks on vessels in 96 hours, maritime centre says.", "UKMTO"),
    (23, "NEW DELHI", "Pakistan minister to lead delegation to SCO dialogue.", "The Hindu"),
    (24, "DOHA", "U17 World Cup: Australia stuns Argentina 2-0.", "FIFA"),
    (25, "SOUTH AFRICA", "Harmer spins Proteas to Test win; Bavuma sets record.", "ICC"),
    (26, "HONG KONG", "Badminton Open semifinals decided.", "BWF"),
    (27, "TAIPEI", "Short-sell curbs take effect; two Russian bombers tracked.", "Reuters"),
    (28, "TURIN", "Alcaraz-Cobolli & Medvedev-Tiafoe close ATP Finals groups.", "ATP"),
    (29, "LOS ANGELES", "Thomas Markle ruled fit to stand trial.", "BBC"),
    (30, "WELLINGTON", "Nicholls 175* in 216-run stand with Phillips.", "ICC"),
    (31, "AL-DAHI, ISRAEL", "Mosque torched in northern Israel; Hebrew graffiti; backlash against Netanyahu.", "One Turn"),
    (32, "EUROPE", "Youth strike in 25+ countries over living costs and militarisation.", "One Turn"),
    (33, "WASHINGTON", "Trump open to NATO-like security guarantees for Ukraine.", "World Times Daily"),
    (34, "WASHINGTON", "Trump pardons late baseball great Pete Rose.", "awlaws"),
    (35, "BOGOT\u00c1", "Colombians protest tax plans amid US military presence row.", "World Times Daily"),
    (36, "LILONGWE", "Malawi fuel crisis sparks chaos nationwide.", "World Times Daily"),
    (37, "GAZA", "Civil Defence struggles as vehicles break down.", "World Times Daily"),
    (38, "OTTAWA", "Tim Hortons faces criticism over Israeli data-sharing deal.", "awlaws"),
    (39, "WASHINGTON", "DOJ drops Alaska midterms Senate certification suit as 'moot'.", "awlaws"),
    (40, "BERLIN", "Zelenskyy meets German, British and French officials.", "nhoq"),
    (41, "SYDNEY", "AFP charges Ingleburn man, 35, over alleged car-bomb research.", "The Register AU"),
    (42, "BRAZIL", "Violent deaths hit series low, down 12.2% in Jan-Oct.", "1stHeadlines"),
    (43, "NEW YORK", "Wall Street falls 2% as Fed hike fears grow.", "1stHeadlines"),
    (44, "S\u00c3O PAULO", "Markets shut as real hits 5.93 to the dollar.", "1stHeadlines"),
    (45, "ALGIERS", "World Bank sees Algeria growth at 3.7%.", "1stHeadlines"),
    (46, "SANTIAGO", "Fuel relief bill may cost $813m.", "1stHeadlines"),
]

DATECHECK = [
    "Trump-Xi-Putin Shenzhen summit + nuclear declaration",
    "Anthropic $83bn IPO pricing & Nasdaq debut (+17%, close $97.17)",
    "ICJ Myanmar Rohingya genocide verdict (9-6)",
    "GTA VI midnight launch",
    "$190.4m Van Gogh sale",
    "Voyager 1 one-light-day confirmation",
    "Senate 48-51 Iran war-powers vote",
    "Austrian & Dutch embassies damaged in Kyiv strikes",
    "Bukele registers for third-term bid (Feb 2027 vote)",
    "Fiona the hippo dies, 9, after swallowing a visitor's hat",
    "Pentagon: Iran war cost $48.3bn (testimony Thu)",
    "UK & Norway fund \u00a3100m+ for two fast attack boats for Ukraine",
    "Indonesia passes asset-forfeiture law (18-year wait)",
    "Migrant boat sinks off Senegal \u2014 4 dead, dozens missing",
]

# lon/lat of pinned places 1-12 (5 = Mercury, in space)
PINS = {1: (85, 20), 2: (30, 50), 3: (30, 37), 4: (130, 37), 6: (4, 51),
        7: (139, 36), 8: (116, 40), 9: (175, -41), 10: (12, 42),
        11: (2, 41), 12: (-55, -12)}

# Pixel nudges so clustered pins (Europe, East Asia) do not overlap.
PIN_OFFSET = {2: (14, -16), 3: (20, 10), 4: (8, -14), 6: (-24, -14),
              7: (22, 10), 8: (-14, -6), 10: (2, 16), 11: (-26, 10)}

# Simplified continent outlines in (lon, lat), for the dot-matrix map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-55, 60),
     (-60, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-72, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (0, 48), (5, 58), (10, 58), (18, 56), (21, 55),
     (28, 60), (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (23, 40),
     (19, 42), (12, 44), (3, 42), (-2, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -15), (35, -25), (28, -33), (20, -35),
     (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5), (-13, 8)],
    [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (160, 70),
     (178, 66), (162, 60), (158, 52), (142, 45), (135, 35), (127, 33),
     (120, 25), (108, 18), (105, 10), (100, 8), (95, 16), (90, 22),
     (80, 15), (77, 8), (70, 20), (60, 25), (50, 29), (48, 30), (43, 38),
     (40, 45)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (136, -12), (132, -12), (126, -14),
     (122, -17), (114, -22)],
]


def inside_poly(lon, lat, poly):
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = (x2 - x1) * (lat - y1) / (y2 - y1) + x1
            if lon < xin:
                inside = not inside
    return inside


def on_land(lon, lat):
    return any(inside_poly(lon, lat, c) for c in CONTINENTS)

# ---------------------------------------------------------------- art
def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 58, 74))
    # tan coast on the left, sea on the right
    d.polygon([(x, y), (x + 62, y), (x + 44, y + h), (x, y + h)], fill=(214, 196, 150))
    d.polygon([(x, y), (x + 62, y), (x + 44, y + h), (x, y + h)], outline=(120, 100, 60))
    d.text((x + 6, y + 4), "INDIA", font=F(SANS_B, 8), fill=(90, 70, 40))
    d.text((x + w - 78, y + h - 14), "BAY OF BENGAL", font=F(SANS_B, 8), fill=(150, 200, 210))
    cx, cy = x + w - 105, y + h // 2 - 2
    for r, col in ((30, (255, 255, 255)), (23, (200, 230, 235)),
                   (16, (255, 255, 255)), (9, (160, 210, 220))):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255))
    # landfall point on the coast
    d.ellipse([x + 48, cy - 4, x + 56, cy + 4], fill=RED, outline=(255, 255, 255))
    d.line([x + 52, cy, cx - 8, cy], fill=RED, width=2)
    d.text((x + 8, y + h - 15), "GOPALPUR", font=F(SANS_B, 8), fill=(90, 70, 40))


def art_missiles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # skyline
    heights = [26, 38, 22, 44, 30, 40, 24]
    bx = x
    for hh in heights:
        bw = w // 7
        d.rectangle([bx, y + h - hh, bx + bw - 3, y + h], fill=(8, 18, 36))
        for wy in range(y + h - hh + 5, y + h - 4, 8):
            d.rectangle([bx + 4, wy, bx + 8, wy + 4], fill=(255, 190, 60))
        bx += bw
    # missile trails arcing down onto the skyline
    for sx, ex, col in ((x + 30, x + 90, (255, 120, 40)),
                        (x + 130, x + 190, (255, 160, 60)),
                        (x + 220, x + 280, (255, 100, 30))):
        pts = []
        for t in range(0, 21):
            f = t / 20.0
            px = sx + (ex - sx) * f
            py = y + 18 + (y + h - 26 - (y + 18)) * f * f
            pts.append((px, py))
        d.line(pts, fill=col, width=3)
        d.ellipse([ex - 4, y + h - 30, ex + 4, y + h - 22], fill=(255, 200, 80),
                  outline=col)
    d.text((x + 6, y + 4), "OVERNIGHT  \u00b7  BALLISTIC MISSILES", font=F(SANS_B, 8), fill=(255, 255, 255))


def art_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 44, 66))
    d.text((x + 6, y + 4), "UN CLIMATE SUMMIT", font=F(SANS_B, 8), fill=(190, 220, 230))
    # globe, lower-left
    cx, cy, r = x + 66, y + 34, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 160, 190),
              outline=(255, 255, 255), width=2)
    d.ellipse([cx - 10, cy - 11, cx + 2, cy - 1], fill=(90, 180, 110))
    d.ellipse([cx - 2, cy + 3, cx + 12, cy + 13], fill=(90, 180, 110))
    d.ellipse([cx + 7, cy - 14, cx + 15, cy - 5], fill=(90, 180, 110))
    # thermometer
    tx = x + 138
    d.rounded_rectangle([tx, y + 8, tx + 12, y + h - 12], 6, fill=(255, 255, 255))
    d.rectangle([tx + 3, y + 12, tx + 9, y + h - 22], fill=RED)
    d.ellipse([tx - 4, y + h - 22, tx + 16, y + h - 2], fill=RED,
              outline=(255, 255, 255), width=2)
    # red banner
    d.rectangle([x + 178, y + 8, x + w - 8, y + 42], fill=RED)
    d.text((x + 186, y + 11), "ANTALYA \u00b7 NOV 20", font=F(SANS_B, 9), fill=(255, 255, 255))
    d.text((x + 186, y + 23), "COP31", font=F(SERIF_B, 14), fill=(255, 255, 255))
    d.text((x + w - 118, y + 46), "$120BN FINANCE GAP", font=F(SANS_B, 8), fill=GOLD_LT)


ART = {1: art_cyclone, 2: art_missiles, 3: art_cop}


def mid_icon(d, kind, x, y, size=16):
    """Tiny white glyph inside a mid-card header band."""
    wcol = (255, 255, 255)
    if kind == "chart":
        d.line([(x, y + 11), (x + 5, y + 6), (x + 10, y + 9), (x + 15, y + 2)],
               fill=wcol, width=2)
        d.polygon([(x + 15, y + 2), (x + 11, y + 2), (x + 15, y + 6)], fill=wcol)
    elif kind == "planet":
        d.ellipse([x + 2, y + 2, x + 12, y + 12], fill=wcol)
        d.line([(x, y + 12), (x + 16, y + 4)], fill=wcol, width=2)
    elif kind == "flags":
        d.line([(x + 4, y + 1), (x + 4, y + 15)], fill=wcol, width=2)
        d.polygon([(x + 4, y + 1), (x + 14, y + 4), (x + 4, y + 7)], fill=wcol)
    elif kind == "bars":
        for i, hh in enumerate((6, 10, 14)):
            d.rectangle([x + 2 + i * 5, y + 15 - hh, x + 5 + i * 5, y + 15], fill=wcol)
    elif kind == "pct":
        d.text((x, y - 1), "%", font=F(SANS_B, 15), fill=wcol)
    elif kind == "ball":
        d.ellipse([x + 3, y + 3, x + 13, y + 13], fill=wcol)
        d.arc([x + 3, y + 3, x + 13, y + 13], 40, 140, fill=RED, width=2)
    elif kind == "mega":
        d.polygon([(x + 1, y + 6), (x + 13, y + 3), (x + 13, y + 9), (x + 1, y + 12)],
                  fill=wcol)
        d.rectangle([x + 13, y + 5, x + 15, y + 10], fill=wcol)
    elif kind == "pill":
        d.rounded_rectangle([x + 1, y + 5, x + 15, y + 11], 3, fill=wcol)
    elif kind == "leaf":
        d.ellipse([x + 2, y + 2, x + 14, y + 14], fill=wcol)
        d.line([(x + 3, y + 13), (x + 13, y + 3)], fill=(60, 90, 24), width=2)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, W - 7, H - 7], outline=NAVY, width=3)
    d.rectangle([10, 10, W - 11, H - 11], outline=GOLD, width=1)

    # ---- masthead top line
    d.text((22, 16), "THE WORLD IN ONE DAY", font=F(SANS_B, 13), fill=NAVY)
    right = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 46 STORIES \u00b7 6 CONTINENTS"
    d.text((W - 22 - d.textlength(right, font=F(SANS_B, 11)), 18),
           right, font=F(SANS_B, 11), fill=RED)
    d.line([22, 36, W - 22, 36], fill=GOLD, width=2)

    # ---- giant title + red subhead
    centre(d, W // 2, 40, "Friday 20 November 2026", F(SERIF_B, 46), NAVY)
    centre(d, W // 2, 92,
           "Cyclone Akvan strikes India \u00b7 Ballistic missiles hit Kyiv \u00b7 "
           "COP31 deadlocked on final day \u00b7 Asian AI sell-off",
           F(SERIF_I, 15), RED)
    d.line([22, 114, W - 22, 114], fill=NAVY, width=2)

    # ---- stat strip: 6 cells
    cell_w = 980 // 6
    y0, y1 = 120, 158
    for i, (big, label) in enumerate(STATS):
        cx0 = 22 + i * cell_w
        centre(d, cx0 + cell_w // 2, y0, big, F(SERIF_B, 21), RED if i % 2 == 0 else NAVY)
        for j, ln in enumerate(wrap(d, label, F(SANS_R, 8), cell_w - 14)):
            centre(d, cx0 + cell_w // 2, y0 + 25 + j * 10, ln, F(SANS_R, 8), GREY)
        if i:
            d.line([cx0, y0 + 2, cx0, y1 - 2], fill=(210, 200, 170), width=1)
    d.line([22, y1, W - 22, y1], fill=(210, 200, 170), width=1)

    # ---- region strip
    d.rectangle([22, 164, W - 22, 184], fill=NAVY)
    centre(d, W // 2, 169, REGION, F(SANS_B, 11), (255, 255, 255))

    # ---- 3 lead cards
    lead_y, lead_h, lead_w, gap = 190, 150, 320, 10
    for i, s in enumerate(LEADS):
        x = 22 + i * (lead_w + gap)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h], fill=PAPER,
                    outline=NAVY, width=1)
        ART[s["n"]](d, x + 1, lead_y + 1, lead_w - 2, 56)
        yy = lead_y + 62
        d.text((x + 8, yy), "%02d \u00b7 %s \u2014 %s" % (s["n"], s["place"], s["topic"]),
               font=F(SANS_B, 9), fill=RED)
        yy += 13
        yy = text_lines(d, x + 8, yy,
                        wrap(d, s["head"], F(SERIF_B, 15), lead_w - 16),
                        F(SERIF_B, 15), NAVY, 17)
        yy = text_lines(d, x + 8, yy + 2,
                        wrap(d, s["body"], F(SANS_R, 9), lead_w - 16),
                        F(SANS_R, 9), INK, 11)
        d.text((x + 8, lead_y + lead_h - 13), "(%s)" % s["src"],
               font=F(SANS_I, 8), fill=GREY)

    # ---- 9 mid cards: 3 x 3
    mid_y0, mid_h, mid_w = 346, 82, 320
    for i, s in enumerate(MIDS):
        r, c = divmod(i, 3)
        x = 22 + c * (mid_w + gap)
        y = mid_y0 + r * (mid_h + 6)
        d.rectangle([x, y, x + mid_w, y + mid_h], fill=PAPER, outline=NAVY, width=1)
        d.rectangle([x, y, x + mid_w, y + 19], fill=s["colour"])
        d.text((x + 7, y + 4), "%02d \u00b7 %s \u2014 %s" % (s["n"], s["place"], s["topic"]),
               font=F(SANS_B, 9), fill=(255, 255, 255))
        mid_icon(d, s["icon"], x + mid_w - 22, y + 2)
        yy = y + 23
        yy = text_lines(d, x + 7, yy,
                        wrap(d, s["head"], F(SERIF_B, 12), mid_w - 14),
                        F(SERIF_B, 12), NAVY, 14)
        yy = text_lines(d, x + 7, yy + 1,
                        wrap(d, s["body"], F(SANS_R, 8), mid_w - 14),
                        F(SANS_R, 8), INK, 10)
        d.text((x + 7, y + mid_h - 11), "(%s)" % s["src"],
               font=F(SANS_I, 7), fill=GREY)

    # ---- dot-matrix world map
    map_y0, map_y1 = 604, 690
    d.rectangle([22, map_y0, W - 22, map_y1], fill=NAVY)
    d.text((30, map_y0 + 6), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=(255, 255, 255))
    d.text((30, map_y0 + 21), "Pins 1-12: lead + mid stories.",
           font=F(SANS_R, 8), fill=(190, 205, 225))
    d.text((30, map_y0 + 32), "Pin 5 is Mercury -",
           font=F(SANS_R, 8), fill=(190, 205, 225))
    d.text((30, map_y0 + 43), "in space, not on Earth.",
           font=F(SANS_R, 8), fill=(190, 205, 225))
    d.text((30, map_y0 + 60), "Dots = land.", font=F(SANS_I, 8), fill=GOLD_LT)
    mx0, mx1, my0, my1 = 300, 724, map_y0 + 4, map_y1 - 4
    step = 6
    for gy in range(my0, my1, step):
        lat = 75 - (gy - my0) / max(1, (my1 - my0)) * 130
        for gx in range(mx0, mx1, step):
            lon = -180 + (gx - mx0) / max(1, (mx1 - mx0)) * 360
            if on_land(lon, lat):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(150, 175, 205))
    for n, (lon, lat) in PINS.items():
        px = int(mx0 + (lon + 180) / 360 * (mx1 - mx0))
        py = int(my0 + (75 - lat) / 130 * (my1 - my0))
        # spread clustered pins so numbers stay legible; dot marks the true spot
        ox, oy = PIN_OFFSET.get(n, (0, 0))
        if (ox, oy) != (0, 0):
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
            d.line([px, py, px + ox, py + oy], fill=(255, 255, 255), width=1)
        px, py = px + ox, py + oy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        num = str(n)
        d.text((px - d.textlength(num, font=F(SANS_B, 8)) / 2, py - 6),
               num, font=F(SANS_B, 8), fill=(255, 255, 255))
    # pin 5: Mercury star, top-right of the map panel (label lives in the key)
    sx, sy = 748, map_y0 + 14
    d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=GOLD_LT, outline=(255, 255, 255), width=1)
    d.text((sx - 3, sy - 6), "5", font=F(SANS_B, 8), fill=NAVY)
    # right-hand pin key
    key = ["1 Odisha", "2 Kyiv", "3 Antalya", "4 Seoul/Tokyo", "5 Mercury",
           "6 Brussels", "7 Tokyo", "8 Beijing", "9 Wellington", "10 Rome",
           "11 Barcelona", "12 Mato Grosso"]
    kx = 776
    for i, k in enumerate(key):
        yy = map_y0 + 6 + (i % 6) * 12
        xx = kx + (i // 6) * 104
        d.text((xx, yy), k, font=F(SANS_R, 8), fill=(220, 228, 240))
    d.text((30, map_y1 - 12), "", font=F(SANS_R, 8), fill=(255, 255, 255))

    # ---- also on: 34 one-liners, two columns
    ay = 698
    d.text((22, ay), "ALSO ON FRIDAY 20 NOVEMBER \u2014 34 MORE STORIES",
           font=F(SANS_B, 11), fill=NAVY)
    d.line([22, ay + 16, W - 22, ay + 16], fill=GOLD, width=1)
    col_w = 485
    row_h = 9
    f_one = F(SANS_R, 8)
    f_one_b = F(SANS_B, 8)
    for i, (n, place, head, src) in enumerate(ONELINERS):
        col, row = divmod(i, 17)
        x = 22 + col * (col_w + 10)
        y = ay + 20 + row * row_h
        num = "%d. " % n
        d.text((x, y), num, font=f_one_b, fill=RED)
        nx = x + d.textlength(num, font=f_one_b)
        d.text((nx, y), "%s \u2014 %s (%s)" % (place, head, src),
               font=f_one, fill=INK)

    # ---- date check box
    dy0 = 872
    d.rectangle([22, dy0, W - 22, 962], outline=RED, width=2)
    d.rectangle([22, dy0, W - 22, dy0 + 18], fill=RED)
    d.text((30, dy0 + 4), "DATE CHECK \u2014 NOT FRIDAY 20 NOVEMBER",
           font=F(SANS_B, 10), fill=(255, 255, 255))
    intro = "First reported Thursday 19 Nov, so NOT shown as Friday's news:"
    body = intro + "  " + " \u00b7 ".join(DATECHECK) + "."
    yy = text_lines(d, 30, dy0 + 22,
                    wrap(d, body, F(SANS_R, 9), W - 60), F(SANS_R, 9), INK, 12)

    # ---- footer
    fy = 970
    centre(d, W // 2, fy,
           "Every story here happened, or was first reported, on Friday 20 November 2026 "
           "in at least one time zone. Claims are attributed, not stated as fact.",
           F(SANS_I, 8), GREY)
    centre(d, W // 2, fy + 12,
           "Sources: Reuters, AP, AFP, BBC, IMD, UN News, ICC, EORTC, and others \u2014 "
           "full list in SOURCES.md. Original vector drawings.",
           F(SANS_R, 8), GREY)
    return img


def main():
    img = render()
    img.save(OUT, format="PNG", optimize=True)
    print("wrote %s (%dx%d)" % (OUT, W, H))


if __name__ == "__main__":
    main()
