"""Main pipeline: fetch, dedup, classify, generate angles."""

import os
from anthropic import Anthropic
from src.newsapi_fetcher import fetch_newsapi
from src.rss_fetcher import fetch_rss_feeds
from src.database import (
    init_db, insert_articles, get_unclassified_articles,
    update_article_classification, get_top_articles, insert_angles, get_db_stats,
    get_custom_instructions,
)
from src.ai_processor import classify_articles, generate_angles


def run_ingestion(newsapi_key: str) -> dict:
    """Step 1: Fetch from all sources and store with dedup."""
    init_db()
    stats = {"newsapi": 0, "rss": 0, "inserted": 0, "skipped": 0}

    # NewsAPI
    if newsapi_key:
        newsapi_articles = fetch_newsapi(newsapi_key)
        stats["newsapi"] = len(newsapi_articles)
    else:
        newsapi_articles = []
        print("No NewsAPI key provided, skipping NewsAPI fetch.")

    # RSS feeds
    rss_articles = fetch_rss_feeds()
    stats["rss"] = len(rss_articles)

    # Combine and insert with dedup
    all_articles = newsapi_articles + rss_articles
    inserted, skipped = insert_articles(all_articles)
    stats["inserted"] = inserted
    stats["skipped"] = skipped

    print(f"Ingestion complete: {stats['newsapi']} from NewsAPI, {stats['rss']} from RSS")
    print(f"  > {inserted} new articles stored, {skipped} duplicates skipped")
    return stats


def run_classification(anthropic_key: str, batch_size: int = 20) -> dict:
    """Step 2: Classify unclassified articles with Claude."""
    client = Anthropic(api_key=anthropic_key)
    stats = {"classified": 0, "batches": 0}

    while True:
        articles = get_unclassified_articles(limit=batch_size)
        if not articles:
            break

        results = classify_articles(client, articles)
        for result in results:
            try:
                update_article_classification(
                    article_id=result["id"],
                    theme=result["theme"],
                    relevance_score=result["relevance_score"],
                    signal=result.get("signal", ""),
                )
                stats["classified"] += 1
            except (KeyError, TypeError) as e:
                print(f"Skipping malformed classification result: {e}")

        stats["batches"] += 1
        print(f"  Batch {stats['batches']}: classified {len(results)} articles")

    print(f"Classification complete: {stats['classified']} articles classified")
    return stats


def run_angle_generation(anthropic_key: str) -> dict:
    """Step 3: Generate story angles from top articles."""
    client = Anthropic(api_key=anthropic_key)

    top_articles = get_top_articles(min_relevance=0.4, limit=25)
    if not top_articles:
        print("No relevant articles found for angle generation.")
        return {"angles": 0}

    custom_instructions = get_custom_instructions()
    if custom_instructions:
        print(f"Using custom instructions ({len(custom_instructions)} chars)")

    print(f"Generating angles from {len(top_articles)} relevant articles...")
    angles = generate_angles(client, top_articles, custom_instructions=custom_instructions)

    if angles:
        count = insert_angles(angles)
        print(f"Angle generation complete: {count} angles created")
        return {"angles": count}
    else:
        print("No angles generated - check prompt or article quality.")
        return {"angles": 0}


def run_full_pipeline(newsapi_key: str, anthropic_key: str) -> dict:
    """Run the complete pipeline end to end."""
    print("=" * 50)
    print("VOLTA STORY ANGLE GENERATOR - Full Pipeline Run")
    print("=" * 50)

    print("\n[1/3] Ingesting articles...")
    ingestion = run_ingestion(newsapi_key)

    print("\n[2/3] Classifying articles...")
    classification = run_classification(anthropic_key)

    print("\n[3/3] Generating story angles...")
    generation = run_angle_generation(anthropic_key)

    db_stats = get_db_stats()
    print(f"\nPipeline complete. DB now has {db_stats['articles']} articles and {db_stats['angles']} angles.")

    return {"ingestion": ingestion, "classification": classification, "generation": generation, "db": db_stats}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_full_pipeline(
        newsapi_key=os.getenv("NEWSAPI_KEY", ""),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY", ""),
    )
