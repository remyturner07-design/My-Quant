# my-quant

Personal stock screener + approve/reject trading bot. See `SPEC.md` for the
full project spec, phases, and rationale.

## Status: Phase 1 — screener only

No broker connection, no trading. This phase pulls daily price/volume data,
filters a watchlist for liquidity + an established uptrend, then checks the
survivors for a recent news catalyst headline. It prints a candidate list —
nothing is executed automatically.

## Setup

```bash
pip install -r requirements.txt
```

Edit `config/config.yaml` to set your watchlist, thresholds, and catalyst
keywords.

## Run

```bash
python main.py
```

Run daily (e.g. via cron) after market close. Not real-time — free data
sources (yfinance, Google News RSS) lag by minutes to hours.

## Roadmap

- **Phase 1 (this code):** screener + catalyst check, console output only.
- **Phase 2:** wire in Moomoo OpenD paper trading with an approve/reject
  prompt on each candidate.
- **Phase 3:** switch to live trading, only after a trusted paper-trading
  track record. Every live trade still requires manual password confirmation
  via Moomoo — this bot never bypasses that.

See `SPEC.md` for full details, including the testing/backtesting approach
and stop conditions before going live.
