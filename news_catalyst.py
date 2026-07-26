"""
Catalyst detection: pulls free news headlines (Google News RSS, per ticker)
and checks for keyword matches in a recent lookback window.

This is deliberately simple — headline keyword matching, not real analysis.
It's a filter to narrow your attention, not a verdict. Treat every match as
"worth a 2-minute manual look", not "confirmed catalyst".

NOTE: not executed in this sandbox (no network access). Test on your machine.
"""

import feedparser
from datetime import datetime, timedelta, timezone
from urllib.parse import quote


def get_recent_headlines(ticker: str, lookback_days: int) -> list:
    """Fetch recent headlines for a ticker via Google News RSS (free, no key needed)."""
    query = quote(f"{ticker} stock")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    headlines = []
    for entry in feed.entries:
        try:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except (AttributeError, TypeError):
            continue
        if published >= cutoff:
            headlines.append({"title": entry.title, "published": published, "link": entry.link})
    return headlines


def find_catalyst(ticker: str, keywords: list, lookback_days: int) -> dict:
    """Return matched headlines containing any catalyst keyword."""
    headlines = get_recent_headlines(ticker, lookback_days)
    matches = [
        h for h in headlines
        if any(kw.lower() in h["title"].lower() for kw in keywords)
    ]
    return {
        "ticker": ticker,
        "has_catalyst": len(matches) > 0,
        "matched_headlines": matches,
        "all_headlines_checked": len(headlines),
    }
