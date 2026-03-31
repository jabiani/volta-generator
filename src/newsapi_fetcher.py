"""Fetch EV industry news from NewsAPI."""

import requests
from datetime import datetime, timedelta
from typing import Optional


QUERIES = [
    "electric vehicle charging OR EV infrastructure OR EV charging network",
    "ChargePoint OR EVgo OR Blink Charging",
    "EV policy OR charging station regulation OR NEVI program",
]


def fetch_newsapi(api_key: str, days_back: int = 14, max_per_query: int = 30) -> list[dict]:
    """Fetch articles from NewsAPI across multiple query sets."""
    base_url = "https://newsapi.org/v2/everything"
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    all_articles = []

    for query in QUERIES:
        params = {
            "q": query,
            "from": from_date,
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": max_per_query,
            "apiKey": api_key,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for art in data.get("articles", []):
                if art.get("title") and art["title"] != "[Removed]":
                    all_articles.append(normalize_newsapi_article(art))
        except requests.RequestException as e:
            print(f"NewsAPI error for query '{query[:40]}...': {e}")

    return all_articles


def normalize_newsapi_article(raw: dict) -> dict:
    """Normalize a NewsAPI article to our standard format."""
    published = raw.get("publishedAt", "")
    if published:
        try:
            published = datetime.fromisoformat(published.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            published = ""

    return {
        "title": (raw.get("title") or "").strip(),
        "url": raw.get("url", ""),
        "source": raw.get("source", {}).get("name", "Unknown"),
        "published_date": published,
        "summary": (raw.get("description") or "").strip(),
        "raw_content": (raw.get("content") or raw.get("description") or "").strip(),
        "fetched_via": "newsapi",
    }
