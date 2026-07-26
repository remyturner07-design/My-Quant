"""
Screener: pulls free daily price/volume data and filters for liquidity + trend.

NOTE: written and reviewed here but NOT executed/tested in this environment
(no network access in this sandbox). Run and debug this on your own machine
via Claude Code, which will have the network access needed to actually hit
Yahoo Finance and iterate on any errors.
"""

import yfinance as yf
import pandas as pd
from dataclasses import dataclass


@dataclass
class ScreenResult:
    ticker: str
    passed: bool
    avg_volume: float
    price: float
    ma_short: float
    ma_long: float
    reasons: list


def screen_ticker(ticker: str, min_avg_volume: int,
                   ma_short_days: int, ma_long_days: int) -> ScreenResult:
    """Pull ~1 year of daily history and check liquidity + trend conditions."""
    hist = yf.Ticker(ticker).history(period="1y", interval="1d")

    if hist.empty or len(hist) < ma_long_days:
        return ScreenResult(ticker, False, 0, 0, 0, 0, ["insufficient data"])

    avg_volume = hist["Volume"].tail(20).mean()
    price = hist["Close"].iloc[-1]
    ma_short = hist["Close"].tail(ma_short_days).mean()
    ma_long = hist["Close"].tail(ma_long_days).mean()

    reasons = []
    passed = True

    if avg_volume < min_avg_volume:
        passed = False
        reasons.append(f"avg volume {avg_volume:,.0f} below threshold {min_avg_volume:,.0f}")

    if not (price > ma_short > ma_long):
        passed = False
        reasons.append(
            f"not in established uptrend (price {price:.2f}, "
            f"{ma_short_days}d MA {ma_short:.2f}, {ma_long_days}d MA {ma_long:.2f})"
        )

    if passed:
        reasons.append("passed liquidity and trend filters")

    return ScreenResult(ticker, passed, avg_volume, price, ma_short, ma_long, reasons)


def screen_watchlist(tickers: list, thresholds: dict) -> list:
    results = []
    for t in tickers:
        try:
            results.append(screen_ticker(
                t,
                thresholds["min_avg_daily_volume"],
                thresholds["trend_short_ma_days"],
                thresholds["trend_long_ma_days"],
            ))
        except Exception as e:
            results.append(ScreenResult(t, False, 0, 0, 0, 0, [f"error: {e}"]))
    return results
