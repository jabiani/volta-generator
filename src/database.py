"""SQLite database for articles and generated angles."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from rapidfuzz import fuzz


DB_PATH = Path(__file__).parent.parent / "data" / "volta.db"
DEDUP_THRESHOLD = 85


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE,
            source TEXT,
            published_date TEXT,
            summary TEXT,
            raw_content TEXT,
            theme TEXT,
            relevance_score REAL DEFAULT 0,
            signal TEXT,
            fetched_via TEXT,
            ingested_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS angles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            rationale TEXT,
            news_peg TEXT,
            outlet_type TEXT,
            outlet_rationale TEXT,
            urgency TEXT DEFAULT 'medium',
            used INTEGER DEFAULT 0,
            source_article_ids TEXT DEFAULT '[]',
            generated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_articles_theme ON articles(theme);
        CREATE INDEX IF NOT EXISTS idx_articles_relevance ON articles(relevance_score);
        CREATE INDEX IF NOT EXISTS idx_angles_urgency ON angles(urgency);
        CREATE INDEX IF NOT EXISTS idx_angles_outlet ON angles(outlet_type);

        CREATE TABLE IF NOT EXISTS blocked_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL UNIQUE,
            reason TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Migration: add 'used' column for existing databases
    try:
        conn.execute("ALTER TABLE angles ADD COLUMN used INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.close()


def is_duplicate(title: str, conn: sqlite3.Connection, batch_titles: list[str] = None) -> bool:
    """Check if a similar article title already exists using fuzzy matching."""
    title_lower = title.lower()
    # Check against current batch
    for existing_title in (batch_titles or []):
        score = max(fuzz.ratio(title_lower, existing_title.lower()),
                    fuzz.partial_ratio(title_lower, existing_title.lower()))
        if score >= DEDUP_THRESHOLD:
            return True
    # Check against database
    existing = conn.execute("SELECT title FROM articles").fetchall()
    for row in existing:
        score = max(fuzz.ratio(title_lower, row["title"].lower()),
                    fuzz.partial_ratio(title_lower, row["title"].lower()))
        if score >= DEDUP_THRESHOLD:
            return True
    return False


def insert_articles(articles: list[dict]) -> tuple[int, int]:
    """Insert articles with dedup. Returns (inserted, skipped) counts."""
    conn = get_connection()
    inserted, skipped = 0, 0
    batch_titles = []

    for art in articles:
        if not art.get("title"):
            skipped += 1
            continue
        if is_blocked(art["title"], art.get("summary", "")):
            skipped += 1
            continue
        if is_duplicate(art["title"], conn, batch_titles):
            skipped += 1
            continue
        try:
            conn.execute(
                """INSERT INTO articles (title, url, source, published_date, summary, raw_content, fetched_via)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (art["title"], art.get("url"), art.get("source"), art.get("published_date"),
                 art.get("summary"), art.get("raw_content"), art.get("fetched_via")),
            )
            inserted += 1
            batch_titles.append(art["title"])
        except sqlite3.IntegrityError:
            skipped += 1

    conn.commit()
    conn.close()
    return inserted, skipped


def get_unclassified_articles(limit: int = 50) -> list[dict]:
    """Get articles that haven't been classified yet."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM articles WHERE theme IS NULL ORDER BY ingested_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_article_classification(article_id: int, theme: str, relevance_score: float, signal: str):
    """Update an article with classification results."""
    conn = get_connection()
    conn.execute(
        "UPDATE articles SET theme = ?, relevance_score = ?, signal = ? WHERE id = ?",
        (theme, relevance_score, signal, article_id),
    )
    conn.commit()
    conn.close()


def get_top_articles(min_relevance: float = 0.4, limit: int = 30) -> list[dict]:
    """Get the most relevant classified articles for angle generation."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM articles
           WHERE theme IS NOT NULL AND relevance_score >= ?
           ORDER BY relevance_score DESC, published_date DESC
           LIMIT ?""",
        (min_relevance, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_angles(angles: list[dict]) -> int:
    """Insert generated angles. Returns count inserted."""
    conn = get_connection()
    count = 0
    for angle in angles:
        conn.execute(
            """INSERT INTO angles (headline, rationale, news_peg, outlet_type, outlet_rationale, urgency, source_article_ids)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (angle["headline"], angle.get("rationale"), angle.get("news_peg"),
             angle.get("outlet_type"), angle.get("outlet_rationale"),
             angle.get("urgency", "medium"),
             json.dumps(angle.get("source_article_ids", []))),
        )
        count += 1
    conn.commit()
    conn.close()
    return count


def get_angles(outlet_type: str = None, urgency: str = None) -> list[dict]:
    """Get generated angles with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM angles WHERE 1=1"
    params = []
    if outlet_type:
        query += " AND outlet_type = ?"
        params.append(outlet_type)
    if urgency:
        query += " AND urgency = ?"
        params.append(urgency)
    query += " ORDER BY generated_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_angle_used(angle_id: int, used: bool):
    """Mark an angle as used/unused."""
    conn = get_connection()
    conn.execute("UPDATE angles SET used = ? WHERE id = ?", (1 if used else 0, angle_id))
    conn.commit()
    conn.close()


def get_articles_by_ids(ids: list[int]) -> list[dict]:
    """Get articles by their IDs."""
    if not ids:
        return []
    conn = get_connection()
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(f"SELECT * FROM articles WHERE id IN ({placeholders})", ids).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_db_stats() -> dict:
    """Get counts for dashboard display."""
    conn = get_connection()
    article_count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    classified_count = conn.execute("SELECT COUNT(*) FROM articles WHERE theme IS NOT NULL").fetchone()[0]
    angle_count = conn.execute("SELECT COUNT(*) FROM angles").fetchone()[0]
    sources = conn.execute("SELECT DISTINCT source FROM articles").fetchall()
    conn.close()
    return {
        "articles": article_count,
        "classified": classified_count,
        "angles": angle_count,
        "sources": [r[0] for r in sources],
    }


# --- Feedback: Blocked Terms ---

def add_blocked_term(term: str, reason: str = ""):
    """Add a term to the block list. Articles matching this term will be filtered out."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO blocked_terms (term, reason) VALUES (?, ?)",
            (term.lower().strip(), reason),
        )
        conn.commit()
    finally:
        conn.close()


def remove_blocked_term(term_id: int):
    """Remove a term from the block list."""
    conn = get_connection()
    conn.execute("DELETE FROM blocked_terms WHERE id = ?", (term_id,))
    conn.commit()
    conn.close()


def get_blocked_terms() -> list[dict]:
    """Get all blocked terms."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM blocked_terms ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_blocked(title: str, summary: str = "") -> bool:
    """Check if an article matches any blocked term."""
    conn = get_connection()
    terms = conn.execute("SELECT term FROM blocked_terms").fetchall()
    conn.close()
    text = f"{title} {summary}".lower()
    return any(t["term"] in text for t in terms)


# --- Feedback: Custom Instructions ---

def set_custom_instructions(text: str):
    """Save custom prompt instructions from the PR team."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO settings (key, value, updated_at) VALUES ('custom_instructions', ?, datetime('now'))
           ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
        (text, text),
    )
    conn.commit()
    conn.close()


def get_custom_instructions() -> str:
    """Get the current custom prompt instructions."""
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = 'custom_instructions'").fetchone()
    conn.close()
    return row["value"] if row else ""


# --- History queries ---

def get_all_angles() -> list[dict]:
    """Get all angles ever generated, ordered by date."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM angles ORDER BY generated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_angles_by_month() -> list[dict]:
    """Get angle counts grouped by month, with pitched counts."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            strftime('%Y-%m', generated_at) as month,
            COUNT(*) as total,
            SUM(CASE WHEN used = 1 THEN 1 ELSE 0 END) as pitched
        FROM angles
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_articles_by_month() -> list[dict]:
    """Get article counts grouped by month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            strftime('%Y-%m', published_date) as month,
            COUNT(*) as total,
            COUNT(DISTINCT source) as sources
        FROM articles
        WHERE published_date IS NOT NULL AND published_date != ''
        GROUP BY month
        ORDER BY month ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_outlet_breakdown() -> list[dict]:
    """Get angle counts by outlet type with pitched ratio."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            outlet_type,
            COUNT(*) as total,
            SUM(CASE WHEN used = 1 THEN 1 ELSE 0 END) as pitched
        FROM angles
        GROUP BY outlet_type
        ORDER BY total DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
