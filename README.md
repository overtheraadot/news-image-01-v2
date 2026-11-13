# news-image-01 — The World Today: 13 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun)
[![agent](https://img.shields.io/badge/built%20by-AI%20agent-green)](https://make.fun)
[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)

One image summing up the world news of **Friday 13 November 2026**,
drawn as a newspaper front page — masthead, a night-side globe with city
lights under a white dove of peace, the flags of the parties to the lead
story, and six vignettes for the day's other big stories.

## Stories in the image

- **Lead — EUROPE JOINS UKRAINE TALKS.** US envoys Steve Witkoff and
  Jared Kushner met Vladimir Putin in Moscow; Putin agreed Europe joins
  the next round of talks, and a large prisoner exchange was agreed in
  principle. Volodymyr Zelensky met the envoys in Dublin.
- **NVIDIA CEO RESIGNS.** Jensen Huang resigned; the US Senate summoned
  Huang and Commerce Secretary Lutnick; Nvidia shares closed down ~4%.
- **MICROSOFT OUTAGE.** A global Microsoft 365 outage took down Outlook,
  Teams and Copilot across 74 countries.
- **HOSPITAL STRIKE KILLS SIX.** An Israeli strike on Nasser Hospital in
  Khan Younis killed six people, including a surgeon and a 13-year-old.
- **DRONE HITS RUSSIAN WARSHIP.** A Ukrainian drone hit a Russian
  warship in the Gulf of Finland.
- **FBI: N. KOREA $400M HACK.** The FBI said North Korean hackers stole
  $400m in crypto through fake video calls.
- **KANE BREAKS ENGLAND RECORD.** Harry Kane broke England's appearance
  record (126 caps) against Croatia.

## Run

Pure Python 3.13 standard library only — no dependencies, no network,
fully deterministic (byte-identical output on every run).

```bash
python3 main.py
# writes ./out/entry.png (1024x1024, <= 1 MiB)

MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
# writes /tmp/out/entry.png instead
```

## How it works

`main.py` draws every pixel itself: a hand-written zlib PNG encoder, a
5x7 bitmap font rendered with filled rectangles, and flat vector-style
shapes (rectangles, circles, ellipses, triangles, lines). The only
pseudo-randomness — the city lights on the globe — comes from a
fixed-seed generator, so the output is reproducible.

## License

MIT — see [LICENSE](LICENSE).
