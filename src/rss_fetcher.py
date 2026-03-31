"""Fetch EV industry news from RSS feeds."""

import feedparser
from datetime import datetime
from time import mktime
from typing import Optional
import re


FEEDS = {
    "Electrek": "https://electrek.co/feed/",
    "Green Car Reports": "https://www.greencarreports.com/rss",
    "InsideEVs": "https://insideevs.com/rss/news/",
    "CleanTechnica": "https://cleantechnica.com/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
}

# Keywords to filter general feeds (TechCrunch) for relevance
EV_KEYWORDS = [
    "ev ", "electric vehicle", "charging", "charger", "chargepoint", "evgo",
    "blink", "tesla", "battery", "grid", "clean energy", "infrastructure",
    "nevi", "volt", "electrif", "renewable", "utility", "power grid",
]


def fetch_rss_feeds(feeds: Optional[dict] = None) -> list[dict]:
    """Fetch and normalize articles from all RSS feeds."""
    feeds = feeds or FEEDS
    all_articles = []

    for source_name, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            is_general = source_name in ("TechCrunch",)

            for entry in feed.entries[:30]:
                article = normalize_rss_entry(entry, source_name)
                if not article["title"]:
                    continue
                if is_general and not is_ev_relevant(article):
                    continue
                all_articles.append(article)
        except Exception as e:
            print(f"RSS error for {source_name}: {e}")

    return all_articles


def normalize_rss_entry(entry: dict, source_name: str) -> dict:
    """Normalize an RSS feed entry to our standard format."""
    published = ""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            published = datetime.fromtimestamp(mktime(entry.published_parsed)).strftime("%Y-%m-%d")
        except (ValueError, TypeError, OverflowError):
            published = ""

    summary = entry.get("summary", "")
    summary = re.sub(r"<[^>]+>", "", summary).strip()
    if len(summary) > 500:
        summary = summary[:497] + "..."

    return {
        "title": (entry.get("title") or "").strip(),
        "url": entry.get("link", ""),
        "source": source_name,
        "published_date": published,
        "summary": summary,
        "raw_content": summary,
        "fetched_via": "rss",
    }


def is_ev_relevant(article: dict) -> bool:
    """Check if an article from a general feed is EV-relevant."""
    text = f"{article['title']} {article['summary']}".lower()
    return any(kw in text for kw in EV_KEYWORDS)
