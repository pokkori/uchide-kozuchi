"""
database.py  ― SQLite スキーマ管理・CRUD
"""
import sqlite3
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class InvestmentDB:
    def __init__(self, db_path: str = "output/investment.db"):
        self.db_path = db_path
        self._init()

    # ── 初期化 ─────────────────────────────────────────────────

    def _init(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS price_snapshots (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker      TEXT NOT NULL,
                    name        TEXT,
                    price       REAL,
                    change_pct  REAL,
                    volume      INTEGER,
                    asset_type  TEXT,
                    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS news_sentiment (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    title        TEXT NOT NULL,
                    url          TEXT UNIQUE NOT NULL,
                    sentiment    TEXT,
                    score        INTEGER,
                    summary      TEXT,
                    related_tickers TEXT,
                    published    TEXT,
                    analyzed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_price_ticker
                    ON price_snapshots(ticker, captured_at DESC);

                CREATE INDEX IF NOT EXISTS idx_news_score
                    ON news_sentiment(score DESC, analyzed_at DESC);
            ''')

    # ── 株価スナップショット ───────────────────────────────────

    def save_price(self, ticker: str, name: str, price: float,
                   change_pct: float, volume: int, asset_type: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO price_snapshots "
                "(ticker, name, price, change_pct, volume, asset_type) "
                "VALUES (?,?,?,?,?,?)",
                (ticker, name, price, change_pct, volume, asset_type)
            )

    def get_latest_prices(self) -> List[Dict]:
        """各銘柄の最新価格を1件ずつ返す"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('''
                SELECT p.*
                FROM price_snapshots p
                INNER JOIN (
                    SELECT ticker, MAX(captured_at) AS max_at
                    FROM price_snapshots
                    GROUP BY ticker
                ) latest ON p.ticker = latest.ticker
                         AND p.captured_at = latest.max_at
                ORDER BY p.ticker
            ''').fetchall()
        return [dict(r) for r in rows]

    # ── ニュースセンチメント ──────────────────────────────────

    def is_url_analyzed(self, url: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM news_sentiment WHERE url=?", (url,)
            ).fetchone()
        return row is not None

    def save_news(self, title: str, url: str, sentiment: str,
                  score: int, summary: str, related_tickers: List[str],
                  published: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO news_sentiment "
                "(title, url, sentiment, score, summary, related_tickers, published) "
                "VALUES (?,?,?,?,?,?,?)",
                (title, url, sentiment, score, summary,
                 ",".join(related_tickers), published)
            )

    def get_recent_news(self, limit: int = 50) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('''
                SELECT * FROM news_sentiment
                ORDER BY score DESC, analyzed_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()
        return [dict(r) for r in rows]

    def get_alert_news(self, threshold: int = 75) -> List[Dict]:
        """高スコアニュースのみ返す"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('''
                SELECT * FROM news_sentiment
                WHERE score >= ?
                ORDER BY analyzed_at DESC
                LIMIT 20
            ''', (threshold,)).fetchall()
        return [dict(r) for r in rows]
