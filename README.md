# 13 November 2026 — The World Today

[![make.fun](https://img.shields.io/badge/make.fun-news--image--01-1B2A4A)](https://make.fun)
[![bounty](https://img.shields.io/badge/bounty-%24250-B02E2E)](https://make.fun)
[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

One image summing up the world news of Friday 13 November 2026, drawn
as a magazine front page by a single Python program. The masthead
carries the date, a globe with a dove and three flags carries the lead
story, and a 2 × 3 grid of vignettes — each with a short bold label set
in a hand-built 5×7 bitmap font — carries the rest of the day.

## The stories

- **Lead — globe, dove, flags: "EUROPE JOINS UKRAINE TALKS".** US
  envoys Steve Witkoff and Jared Kushner met President Putin in Moscow;
  Putin agreed Europe joins the next round, Zelensky met the envoys in
  Dublin, and a large prisoner exchange was agreed in principle.
- **"NVIDIA CEO RESIGNS"** — an empty witness chair, a chip and a red
  down arrow. Jensen Huang resigned; the US Senate summoned Huang and
  Lutnick; shares closed down ~4%.
- **"MICROSOFT OUTAGE"** — a darkened envelope under a warning
  triangle. Microsoft 365 was down worldwide: Outlook, Teams and
  Copilot across 74 countries.
- **"HOSPITAL STRIKE KILLS SIX"** — a hospital block with a white
  cross, and a candle. An Israeli strike on Nasser Hospital, Khan
  Younis, killed six, including a surgeon and a 13-year-old.
- **"DRONE HITS RUSSIAN WARSHIP"** — a warship on a grey sea, smoke
  from the funnel. A Ukrainian drone hit a Russian warship in the Gulf
  of Finland.
- **"FBI: N. KOREA $400M HACK"** — a laptop with a masked face and
  spilling gold coins. The FBI says North Korean hackers stole $400m
  in crypto via fake video calls.
- **"KANE BREAKS ENGLAND RECORD"** — an England footballer in white
  striking the ball. Harry Kane broke England's appearance record
  (126 caps) against Croatia.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024×1024, PNG, well under 1 MiB) into
`$MAKEFUN_OUTPUT_DIR` (default `./out`).

## Determinism

Pure Python 3 standard library (only `zlib` for the PNG encoder), no
network, no files read, no randomness — every run writes byte-identical
output. Verified: two consecutive runs produce the same SHA-256.

## Layout

- Masthead: `13 NOVEMBER 2026` / `THE WORLD TODAY`, red rule.
- Lead: globe (r 140) with continents, latitude/longitude lines, dove
  with olive branch, flags of Ukraine, the EU and the USA, and a navy
  banner with the lead headline.
- Grid: 2 rows × 3 columns, each vignette a flat pictorial scene on a
  newsprint panel with a gold rule and one label line underneath.
- All text is drawn from a 5×7 bitmap font implemented in `main.py`,
  so the labels stay legible even at ~300 px.
