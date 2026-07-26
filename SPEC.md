# Personal Stock Screener + Approve/Reject Trading Bot — Project Spec

## Goal
A tool that runs daily, screens a watchlist of stocks for:
1. **Liquidity** (avg daily volume above a threshold)
2. **Established uptrend** (price trend over 1–3 months, not a single-day spike)
3. **A catalyst** (recent news headline suggesting earnings beat / upgrade / sector
   tailwind — detected from free news headlines, not deep financial analysis)

...then sends you a notification for each candidate, and on your "yes", places a
trade via the Moomoo API. On "no", it does nothing. Nothing trades without your
explicit approval.

## What this is NOT
- Not a system that reliably beats the market. It automates the *process* you'd do
  manually (screen, check, decide) — it doesn't create an edge by itself.
- Not real-time. Free news sources (Google News RSS, Yahoo Finance) lag paid feeds
  by minutes to hours. A stock can already have moved by the time you see the alert.
- Not financial advice generation. The "catalyst" detection is keyword/headline
  matching, not genuine financial analysis — treat every alert as a starting point
  for your own 2-minute check, not a verdict.

## Architecture (all free-tier data)

| Component | Source | Cost | Notes |
|---|---|---|---|
| Price/volume history | `yfinance` (unofficial Yahoo Finance library) | Free | ~15-min delayed, can break if Yahoo changes their site — this is the main fragility point |
| News headlines | Google News RSS + Yahoo Finance RSS per ticker | Free | Headline-level only, no full article parsing needed for keyword matching |
| Trend/liquidity logic | Local Python (pandas) | Free | Runs on your machine |
| Trade execution | Moomoo OpenAPI (OpenD gateway) | Free with brokerage account | Defaults to paper trading; live trades need your manual password confirmation every time — this is a safety feature, not a bug, keep it on |
| Notifications | Start with console/log output → later email or Telegram bot (both free) | Free | Approve/reject prompt |
| Scheduling | Cron job or a simple loop, run once per day after market close | Free | You don't need intraday polling for a 1–3 month trend strategy |

## Build phases

**Phase 1 — Screener only, no broker connection, no trading**
- Pull daily price/volume history for a watchlist (start with ~15-20 tickers you
  choose, e.g. ASX 200 or S&P 500 constituents)
- Filter: avg 20-day volume > threshold (liquidity)
- Filter: price above its 50-day moving average, and 50-day MA above 150-day MA
  (a standard, simple "established uptrend" test)
- Filter: at least one recent headline (last 5 days) containing catalyst keywords
  (earnings, upgrade, raises guidance, contract, beat, etc.)
- Output: a plain list of candidates with the reason each was flagged
- **Test:** run it against historical data and manually sanity-check the output
  against stocks you already know moved for those reasons. No money involved.

**Phase 2 — Paper trading connection**
- Install Moomoo OpenD gateway, connect via the Python SDK
- Wire the Phase 1 output into a notification + approve/reject prompt
- On approval, place a **paper trade** (simulated, not real money)
- **Test:** run for 2-4 weeks on paper, track results in a log, compare to just
  holding an index fund over the same period

**Phase 3 — Live trading (only after Phase 2 has a track record you trust)**
- Same code, switched to live account
- Every trade still requires your manual password confirmation (Moomoo enforces
  this at the API level for live trades — can't be bypassed by the bot)
- Start with small position sizes

## Testing approach at every phase
- **Backtest** the screener logic against 6-12 months of historical data before
  trusting any live signal — did flagged stocks actually outperform afterward?
- **Paper trade** before live, minimum a few weeks
- **Keep a log** of every alert (shown to you) and every decision (approved/rejected)
  and outcome — this is how you find out if the tool has any real value over time
- Set a **stop condition**: e.g. if paper trading underperforms a simple index
  benchmark after 4-6 weeks, that's a signal to revise the logic, not push to live

## What you need to do locally (the one part I can't do from here)
1. Install Python 3.10+ and Moomoo OpenD on your own computer
2. Open a Moomoo account with API access enabled, get paper trading working
3. Run the code below via Claude Code on your machine, where it has network
   access and can see your actual OpenD connection — Claude Code can finish
   wiring the broker connection, debug any local environment issues, and iterate
   from there
4. Everything else (screener logic, backtest, notification logic) is written
   below and ready to hand to Claude Code as a starting point
