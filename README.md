# news-image-01 — The World Today: 13 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

One image summing up the world news of **Friday 13 November 2026** — a
newspaper front page drawn entirely in code: a dove of peace over a night
globe for the Ukraine talks lead, plus six vignettes for the day's other
big stories.

## The stories

| Panel | Story |
| --- | --- |
| Lead | **Europe joins Ukraine talks** — US envoys Witkoff & Kushner met Putin in Moscow; Putin agreed Europe joins the next round; Zelensky met the envoys in Dublin; a large prisoner exchange agreed in principle. |
| 1 | **NVIDIA CEO resigns** — Jensen Huang resigns; the US Senate summons Huang & Lutnick; shares close down ~4%. |
| 2 | **Microsoft outage** — Microsoft 365 global outage: Outlook, Teams and Copilot down across 74 countries. |
| 3 | **Hospital strike kills six** — Israeli strike on Nasser Hospital, Khan Younis, kills six, including a surgeon and a 13-year-old. |
| 4 | **Drone hits Russian warship** — Ukrainian drone hits a Russian warship in the Gulf of Finland. |
| 5 | **FBI: N. Korea $400M hack** — North Korean hackers stole $400m in crypto via fake video calls. |
| 6 | **Kane breaks England record** — Harry Kane breaks England's appearance record (126 caps) vs Croatia. |

## Run

Pure Python 3.13 standard library — no dependencies, no network, no files
read. Deterministic: the output is byte-identical across runs.

```bash
python3 main.py
# writes ./out/entry.png (1024x1024, <= 1 MiB)

# or choose the output directory:
MAKEFUN_OUTPUT_DIR=/path/to/dir python3 main.py
```

Verify determinism:

```bash
MAKEFUN_OUTPUT_DIR=/tmp/run-a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/run-b python3 main.py
sha256sum /tmp/run-a/entry.png /tmp/run-b/entry.png   # identical hashes
```

## How it works

`main.py` implements everything from scratch: a tiny raster canvas
(rectangles, lines, circles, ellipses, triangles), a hand-defined 5x7
bitmap font rendered with filled rectangles, a fixed-seed LCG that scatters
the city lights on the night globe, and a hand-written zlib PNG encoder.
The front page is composed of a masthead, a dove carrying an olive branch
above a night-side globe with the flags of Ukraine, the EU and the USA, a
navy banner, and a 2×3 grid of flat pictorial vignettes with bold labels.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 overtheraadot.
