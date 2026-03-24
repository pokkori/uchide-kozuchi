import sqlite3
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DBManager:
    def __init__(self, db_path: str = "content_data.db"):
        self.db_path = db_path
        self.init_db()
        self._migrate()

    def init_db(self):
        """データベースとテーブルの初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 処理済みURLを記録するテーブル（重複防止）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS processed_urls (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        url          TEXT UNIQUE NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # 評価結果・生成コンテンツを保存するテーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generated_contents (
                        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                        title                TEXT NOT NULL,
                        url                  TEXT NOT NULL,
                        score                INTEGER NOT NULL,
                        summary              TEXT,
                        article_title        TEXT,
                        article_body         TEXT,
                        tweet_text           TEXT,
                        file_path            TEXT,
                        published_platforms  TEXT,
                        created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"データベースの初期化に失敗しました: {e}")

    def _migrate(self):
        """既存DBに新カラムを追加する（冪等）"""
        new_columns = [
            ("article_title",       "TEXT"),
            ("article_body",        "TEXT"),
            ("tweet_text",          "TEXT"),
            ("file_path",           "TEXT"),
            ("published_platforms", "TEXT"),
        ]
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(generated_contents)")
                existing = {row[1] for row in cursor.fetchall()}

                for col_name, col_type in new_columns:
                    if col_name not in existing:
                        cursor.execute(
                            f"ALTER TABLE generated_contents ADD COLUMN {col_name} {col_type}"
                        )
                        logging.info(f"DBマイグレーション: '{col_name}' カラムを追加しました。")
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"DBマイグレーションに失敗しました: {e}")

    def is_url_processed(self, url: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM processed_urls WHERE url = ?', (url,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"URLチェックに失敗しました {url}: {e}")
            return False

    def mark_url_processed(self, url: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR IGNORE INTO processed_urls (url) VALUES (?)', (url,)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"処理済みURLの記録に失敗しました {url}: {e}")

    def save_content(self, title: str, url: str, score: int, summary: str,
                     article_title: str = "", article_body: str = "",
                     tweet_text: str = "", file_path: str = "",
                     published_platforms: List[str] = None):
        """生成されたコンテンツとメタ情報をDBに保存する"""
        platforms_str = ",".join(published_platforms) if published_platforms else ""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO generated_contents
                        (title, url, score, summary,
                         article_title, article_body, tweet_text,
                         file_path, published_platforms)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, url, score, summary,
                      article_title, article_body, tweet_text,
                      file_path, platforms_str))
                conn.commit()
                logging.info(
                    f"DBに保存しました (スコア:{score}, 配信先:{platforms_str}): {title}"
                )
        except sqlite3.Error as e:
            logging.error(f"コンテンツの保存に失敗しました: {e}")
