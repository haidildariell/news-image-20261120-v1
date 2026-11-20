# Friday 20 November 2026: 46 stories, 6 continents, one front page (v1)

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v1/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v1/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A single 1024×1024 front page summing up Friday 20 November 2026 — 46 stories
across 6 continents, rendered by one Python program with Pillow. No network,
no external images: every illustration is drawn from Pillow primitives.

## Layout

- Masthead: "The World in One Day" + giant serif date, red subhead of the day's
  four biggest threads.
- Stat strip: six big numbers (370,000+ evacuated; 3 Dnipro bridges; −7% Asia
  shares; 2.3% Japan CPI; 118 Phillips; 60.7% daraxonrasib response).
- Region strip: Asia-Pacific 11 · Europe 9 · Middle East 4 · Americas 13 ·
  Africa 4 · Oceania 3 · Global 2 = 46.
- 3 illustrated lead cards (Cyclone Akvan, Kyiv barrage, COP31 deadlock) with
  flat vector art: cyclone swirl over a coast, missile trails over a skyline,
  globe + thermometer.
- 9 mid cards with small flat icons (markets, space, EU–UK summit, Japan CPI,
  China rates, cricket, Italian strike, daraxonrasib trial, Chief Raoni).
- Dot-matrix world map "Where It Happened" with numbered pins 1–12 (pin 5 is
  Mercury, in space).
- "Also on Friday 20 November — 34 more stories": numbered one-liners 13–46.
- DATE CHECK box: 14 big stories first reported Thursday 19 Nov, deliberately
  NOT shown as Friday's news.
- Footer: every story happened, or was first reported, on Friday 20 November
  2026 in at least one time zone; claims are attributed, not stated as fact.

## Honesty

- All 46 stories are dated Friday 20 November 2026 in at least one time zone,
  each verified against at least one named source (full list in SOURCES.md).
- Numbers are kept exactly as reported: Akvan winds 70–80 gusting 90 km/h (not
  90–100); 370,000 evacuated (not 300,000); daraxonrasib 60.7% is an early
  trial with no chemo-only comparison — the page never claims it beats chemo
  alone; BepiColombo's orbit insertion is Saturday, its arrival was Friday.
- The DATE CHECK box exists because the previous day's leaderboard leader mixed
  Thursday stories into Friday's page; this entry corrects that.

## Build & run

```bash
python3 build_image.py   # writes entry.png (1024x1024, <=1 MiB, deterministic)
python3 main.py          # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

Run `build_image.py` twice and compare sha256 — the bytes are identical.
