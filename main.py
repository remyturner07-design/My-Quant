"""
Phase 1 entry point: screen watchlist for liquidity + trend, then check
candidates for a news catalyst. Prints results — no trading, no broker
connection yet. Run this daily (e.g. via cron) after market close.

Usage:
    python main.py

NOTE: not executed in this sandbox (no network access). Run via Claude Code
on your own machine, which can install dependencies, run this, and debug
any errors against live data.
"""

import yaml
from screener import screen_watchlist
from news_catalyst import find_catalyst


def main():
    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)

    print("=== Step 1: Liquidity + trend screen ===")
    results = screen_watchlist(config["watchlist"], config["thresholds"])

    passed = [r for r in results if r.passed]
    for r in results:
        status = "PASS" if r.passed else "skip"
        print(f"[{status}] {r.ticker}: {'; '.join(r.reasons)}")

    print(f"\n{len(passed)}/{len(results)} tickers passed liquidity + trend filters.\n")

    print("=== Step 2: Catalyst check on passed tickers ===")
    candidates = []
    for r in passed:
        catalyst = find_catalyst(
            r.ticker,
            config["catalyst_keywords"],
            config["thresholds"]["catalyst_lookback_days"],
        )
        if catalyst["has_catalyst"]:
            candidates.append((r, catalyst))
            print(f"\n{r.ticker} — CATALYST FOUND:")
            for h in catalyst["matched_headlines"]:
                print(f"  - {h['title']} ({h['published'].date()})")
        else:
            print(f"{r.ticker}: no catalyst headline in last "
                  f"{config['thresholds']['catalyst_lookback_days']} days")

    print(f"\n=== {len(candidates)} candidate(s) ready for review ===")
    for r, c in candidates:
        print(f"- {r.ticker}: price {r.price:.2f}, "
              f"avg vol {r.avg_volume:,.0f}, "
              f"{len(c['matched_headlines'])} catalyst headline(s)")

    # Phase 2 will replace this print-out with a notification + approve/reject
    # prompt, and on approval, a paper trade via the Moomoo API.
    # Phase 3 switches the paper trade to a live trade (still requiring your
    # manual password confirmation, enforced by Moomoo itself).


if __name__ == "__main__":
    main()
