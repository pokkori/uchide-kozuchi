"""
publisher.py

生成されたコンテンツを以下の3チャネルへ配信する。
  1. Twitter / X  (tweepy v2 API)
  2. WordPress    (REST API + アプリケーションパスワード)
  3. ファイル出力  (Markdown形式、./output/ ディレクトリ)

各チャネルは .env で認証情報が設定されている場合のみ実行される。
"""

import logging
import os
import re
from datetime import datetime
from typing import List

import requests

import config

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self):
        self._twitter_client = None

    # ── Twitter / X ─────────────────────────────────────────────────────────

    def _get_twitter_client(self):
        if self._twitter_client is not None:
            return self._twitter_client
        if not config.is_twitter_configured():
            return None
        try:
            import tweepy
            self._twitter_client = tweepy.Client(
                consumer_key=config.TWITTER_API_KEY,
                consumer_secret=config.TWITTER_API_SECRET,
                access_token=config.TWITTER_ACCESS_TOKEN,
                access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            )
            return self._twitter_client
        except ImportError:
            logger.error("tweepy がインストールされていません: pip install tweepy")
            return None

    def publish_to_twitter(self, tweet_text: str, source_url: str) -> bool:
        client = self._get_twitter_client()
        if client is None:
            logger.warning("Twitter 認証情報が未設定です。スキップします。")
            return False

        # URL を付加（Tweet全体が280字以内に収まるよう調整）
        url_part = f"\n{source_url}"
        max_body = 280 - len(url_part)
        body = tweet_text[:max_body] if len(tweet_text) > max_body else tweet_text
        full_tweet = body + url_part

        try:
            client.create_tweet(text=full_tweet)
            logger.info("Twitter への投稿が完了しました。")
            return True
        except Exception as e:
            logger.error(f"Twitter 投稿エラー: {e}")
            return False

    # ── WordPress ───────────────────────────────────────────────────────────

    def publish_to_wordpress(self, article_title: str, article_body: str) -> bool:
        if not config.is_wordpress_configured():
            logger.warning("WordPress 認証情報が未設定です。スキップします。")
            return False

        api_url = config.WORDPRESS_URL.rstrip("/") + "/wp-json/wp/v2/posts"
        payload = {
            "title":   article_title,
            "content": article_body,
            "status":  config.WORDPRESS_POST_STATUS,
        }

        try:
            resp = requests.post(
                api_url,
                json=payload,
                auth=(config.WORDPRESS_USERNAME, config.WORDPRESS_APP_PASSWORD),
                timeout=20,
            )
            resp.raise_for_status()
            post_link = resp.json().get("link", "")
            logger.info(f"WordPress への投稿が完了しました: {post_link}")
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(f"WordPress HTTP エラー ({e.response.status_code}): "
                         f"{e.response.text[:300]}")
            return False
        except Exception as e:
            logger.error(f"WordPress 投稿エラー: {e}")
            return False

    # ── ファイル出力 ─────────────────────────────────────────────────────────

    def save_to_file(self, article_title: str, article_body: str,
                     tweet: str, source_url: str) -> str:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = re.sub(r'[\\/:*?"<>|]', "", article_title)[:40].strip()
        filename   = os.path.join(output_dir, f"{timestamp}_{safe_title}.md")

        content = (
            f"# {article_title}\n\n"
            f"{article_body}\n\n"
            "---\n\n"
            f"**元記事:** {source_url}\n\n"
            "**Twitter 投稿文:**\n"
            f"> {tweet}\n"
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"ファイル出力が完了しました: {filename}")
        return filename

    # ── 統合配信 ────────────────────────────────────────────────────────────

    def publish_all(self, article_title: str, article_body: str,
                    tweet: str, source_url: str) -> List[str]:
        """
        設定済みの全チャネルへ配信し、成功したプラットフォーム名のリストを返す。
        ファイル出力は常に実行する。
        """
        published = []

        # ① ファイル出力（常時）
        self.save_to_file(article_title, article_body, tweet, source_url)
        published.append("file")

        # ② Twitter
        if self.publish_to_twitter(tweet, source_url):
            published.append("twitter")

        # ③ WordPress
        if self.publish_to_wordpress(article_title, article_body):
            published.append("wordpress")

        return published
