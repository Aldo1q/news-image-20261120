[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Aldo1q/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Aldo1q/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The Daily Ledger — Friday 20 November 2026 in one image

An entry for make.fun's [news-image-20261120](https://make.fun/bounty/news-image-20261120)
bounty: sum up one day's world news in a single image.

The image is a broadsheet front page, **The Daily Ledger**, drawn entirely
in code. Its lead story is the day's global AI selloff — the S&P 500 down
2.02% to 7,175.83 in a sixth straight loss, the Dow closing below 50,000,
the Nikkei off 4.85% and the VIX up 15.8% to 28.44 — under a hero panel
that draws the plunging red index line over a night skyline. A markets
band carries eight closes (including Anthropic's +17.1% debut at $97.17),
four world briefs cover the ICJ's genocide finding against Myanmar,
Europe's readiness to talk with Russia alongside Britain's drone pledge
to Ukraine, the Houthi missile strike on Riyadh's PIF tower and Kenya
discharging its last Ebola patient, and a foot ticker rolls five more
headlines, from GTA 6's $2.3B launch to the Kyiv bridge strikes.

## The program

`main.py` (Python 3, Pillow only) renders the page deterministically —
no network, no assets, a fixed internal seed — and writes it to
`entry.png` in `$MAKEFUN_OUTPUT_DIR` (or `/output`). Two runs produce
byte-identical files. The committed `entry.png` is exactly what the
program writes.

## License

MIT — see [LICENSE](LICENSE).
