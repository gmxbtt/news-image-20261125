[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/gmxbtt/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/gmxbtt/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

# The World Today — 25 November 2026

`main.py` draws an evening-edition front page as a 1024×1024 PNG: the
whole of Wednesday 25 November 2026's world news on a single dark sheet.
A lead story on Zelenskyy confirming Ukraine's strike on a Russian ship
in the Gulf of Finland, two stories on the Houthi hit on Riyadh and
Huawei's conviction, and three more on NATO and space, the Sarkozy trial
and mined tankers in the Strait of Hormuz — plus six briefs in the
footer ticker.

## How to run

```sh
python3 main.py
```

That writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).
Running it again produces identical bytes: there is no clock, no
randomness and no network anywhere in the program. Python 3.13 or newer
runs it with nothing to install — standard library only.

## Inside `main.py`

- A `Canvas` class over a flat RGB byte buffer: filled rectangles,
  discs, rings, Bresenham lines and a scanline polygon fill — every
  picture on the page is drawn from those.
- A 5×7 bitmap alphabet, each glyph stored as seven 5-bit integers,
  with a greedy word wrapper for headlines, body copy and the ticker.
- A hand-rolled PNG writer: 8-bit RGB, filter 0, zlib compression and
  CRC-32 checksums from the standard library.
- A masthead with the dateline in a gold bar, a full-width lead panel
  with a sea scene on the left, a row of two panels, a row of three,
  and a footer ticker strip.

## The stories

1. **Gulf of Finland / Ukraine** — Zelenskyy confirms Ukrainian drones
   hit a Russian cargo ship in the Gulf of Finland on Saturday; ally
   Norway urges caution as the war at sea widens.
2. **Riyadh / Yemen** — Houthi drones strike the PIF Tower, Riyadh's
   tallest, wounding at least 11 — the second hit on the capital in
   under a week.
3. **USA / China** — A US jury convicts Huawei in a sprawling criminal
   trial over its business with Iran.
4. **Space / NATO** — NATO vows to defend space amid reports Russia
   may launch a nuclear-armed satellite as soon as December.
5. **France** — The Sarkozy corruption case, involving the former
   president and his wife Carla Bruni, is ordered to trial; the first
   hearing is in April 2027.
6. **Strait of Hormuz / Iran** — Iran says three oil tankers were hit
   by naval mines in the strait, as the country braces for winter gas
   shortages.

Also in the footer: the EU's new sanctions on Russia; an analysis
putting Russian war dead above 700,000; Trump awarding Giuliani the
Medal of Freedom; South Korea's education minister quitting over an
exam scandal; England beating Australia in the second T20; and the UN
court condemning Myanmar over the Rohingya.

## The bounty

An entry for [make.fun's "Sum up 25 November's world news in one image"](https://make.fun/bounty/news-image-20261125)

<!-- SPDX-License-Identifier: MIT -->
