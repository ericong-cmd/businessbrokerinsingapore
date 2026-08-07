import sqlite3
import os
import csv
import io
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS listings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id     TEXT,
            source         TEXT    NOT NULL,
            title          TEXT    NOT NULL,
            url            TEXT    NOT NULL,
            asking_price   TEXT,
            revenue        TEXT,
            cash_flow      TEXT,
            ebitda         TEXT,
            location       TEXT,
            industry       TEXT,
            description    TEXT,
            established    TEXT,
            employees      TEXT,
            image_url      TEXT,
            scraped_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active      INTEGER DEFAULT 1,
            UNIQUE(source, url)
        );

        CREATE TABLE IF NOT EXISTS scrape_runs (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            source         TEXT    NOT NULL,
            started_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at   TIMESTAMP,
            listings_found INTEGER DEFAULT 0,
            listings_new   INTEGER DEFAULT 0,
            status         TEXT    DEFAULT 'running',
            error          TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_listings_source   ON listings(source);
        CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(location);
        CREATE INDEX IF NOT EXISTS idx_listings_scraped  ON listings(scraped_at);
        CREATE INDEX IF NOT EXISTS idx_listings_active   ON listings(is_active);
    """)
    conn.commit()
    conn.close()


def upsert_listing(listing_dict: dict) -> bool:
    """Insert or update a listing. Returns True if it was a new record."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO listings
               (listing_id, source, title, url, asking_price, revenue, cash_flow,
                ebitda, location, industry, description, established, employees,
                image_url, scraped_at, updated_at)
               VALUES (:listing_id, :source, :title, :url, :asking_price, :revenue,
                       :cash_flow, :ebitda, :location, :industry, :description,
                       :established, :employees, :image_url,
                       CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
               ON CONFLICT(source, url) DO UPDATE SET
                   title        = excluded.title,
                   asking_price = excluded.asking_price,
                   revenue      = excluded.revenue,
                   cash_flow    = excluded.cash_flow,
                   ebitda       = excluded.ebitda,
                   location     = excluded.location,
                   industry     = excluded.industry,
                   description  = excluded.description,
                   established  = excluded.established,
                   employees    = excluded.employees,
                   image_url    = excluded.image_url,
                   updated_at   = CURRENT_TIMESTAMP,
                   is_active    = 1""",
            {
                'listing_id': listing_dict.get('listing_id'),
                'source':      listing_dict['source'],
                'title':       listing_dict['title'],
                'url':         listing_dict['url'],
                'asking_price': listing_dict.get('asking_price'),
                'revenue':     listing_dict.get('revenue'),
                'cash_flow':   listing_dict.get('cash_flow'),
                'ebitda':      listing_dict.get('ebitda'),
                'location':    listing_dict.get('location'),
                'industry':    listing_dict.get('industry'),
                'description': listing_dict.get('description'),
                'established': listing_dict.get('established'),
                'employees':   listing_dict.get('employees'),
                'image_url':   listing_dict.get('image_url'),
            }
        )
        is_new = cursor.lastrowid and cursor.rowcount > 0
        conn.commit()
        return bool(is_new)
    finally:
        conn.close()


def get_listings(source=None, search=None, location=None, industry=None,
                 active_only=True, limit=500, offset=0):
    conn = get_connection()
    where = ["1=1"]
    params = []
    if active_only:
        where.append("is_active = 1")
    if source:
        where.append("source = ?")
        params.append(source)
    if search:
        where.append("(title LIKE ? OR description LIKE ? OR location LIKE ?)")
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")
    if industry:
        where.append("industry LIKE ?")
        params.append(f"%{industry}%")

    sql = f"""
        SELECT * FROM listings
        WHERE {' AND '.join(where)}
        ORDER BY scraped_at DESC
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(sql, params + [limit, offset]).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_listing_by_id(listing_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM listings WHERE is_active=1").fetchone()[0]
    by_source = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM listings WHERE is_active=1 GROUP BY source"
    ).fetchall()
    last_run = conn.execute(
        "SELECT source, completed_at, listings_found, status "
        "FROM scrape_runs WHERE status='done' ORDER BY completed_at DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return {
        'total': total,
        'by_source': {r['source']: r['cnt'] for r in by_source},
        'last_runs': [dict(r) for r in last_run],
    }


def start_scrape_run(source: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO scrape_runs (source, started_at, status) VALUES (?, CURRENT_TIMESTAMP, 'running')",
        (source,)
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def finish_scrape_run(run_id: int, found: int, new: int, error: str = None):
    conn = get_connection()
    conn.execute(
        """UPDATE scrape_runs SET
           completed_at=CURRENT_TIMESTAMP, listings_found=?, listings_new=?,
           status=?, error=?
           WHERE id=?""",
        (found, new, 'error' if error else 'done', error, run_id)
    )
    conn.commit()
    conn.close()


def get_scrape_run(run_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM scrape_runs WHERE id=?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def export_csv(source=None, search=None) -> str:
    rows = get_listings(source=source, search=search, limit=10000)
    output = io.StringIO()
    if not rows:
        return ""
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
