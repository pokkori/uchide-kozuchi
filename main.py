import logging
import time

import config
from affiliate_manager import AffiliateManager
from article_generator import ArticleGenerator
from db_manager import DBManager
from ollama_client import OllamaClient
from publisher import Publisher
from scraper import TrendScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

RSS_FEEDS = [
    "https://news.yahoo.co.jp/rss/topics/it.xml",
    "https://news.yahoo.co.jp/rss/topics/economy.xml",
    "https://news.yahoo.co.jp/rss/topics/entertainment.xml",
]


def run_pipeline(scraper: TrendScraper, ai_client: OllamaClient,
                 affiliate: AffiliateManager, generator: ArticleGenerator,
                 publisher: Publisher, db: DBManager):
    logging.info("トレンド監視パイプラインを開始します...")

    entries = scraper.fetch_rss_entries(max_entries_per_feed=5)

    for entry in entries:
        title = entry['title']
        url   = entry['link']

        if db.is_url_processed(url):
            logging.debug(f"スキップ(処理済み): {title}")
            continue

        logging.info(f"新規記事を評価中: {title}")
        text_to_evaluate = f"タイトル: {title}\n概要: {entry['summary']}"

        # ── Step 1: 収益性スコア算出 ────────────────────────────
        evaluation = ai_client.evaluate_profitability(text_to_evaluate)
        score   = evaluation.get('score', 0)
        summary = evaluation.get('summary', '')

        if score < config.PROFIT_SCORE_THRESHOLD:
            logging.info(f"スコアが低いためスキップ ({score}): {title}")
            db.mark_url_processed(url)
            continue

        logging.info(f"高スコア ({score}) を検出。コンテンツ生成を開始します。")

        # ── Step 2: アフィリエイト商品を検索 ─────────────────────
        products = affiliate.find_products(keyword=title, max_per_source=2)

        # ── Step 3: 記事本文・Tweet 生成 ──────────────────────────
        article = generator.generate(
            title=title,
            summary=entry['summary'],
            products=products,
        )
        article_title = article['article_title']
        article_body  = article['article_body']
        tweet_text    = article['tweet']

        # ── Step 4: 各チャネルへ配信 ──────────────────────────────
        published_platforms = publisher.publish_all(
            article_title=article_title,
            article_body=article_body,
            tweet=tweet_text,
            source_url=url,
        )

        # ── Step 5: DB 保存 ────────────────────────────────────────
        db.save_content(
            title=title,
            url=url,
            score=score,
            summary=summary,
            article_title=article_title,
            article_body=article_body,
            tweet_text=tweet_text,
            published_platforms=published_platforms,
        )
        db.mark_url_processed(url)

        logging.info(
            f"完了 — 配信先: {', '.join(published_platforms)} | {title}"
        )


if __name__ == "__main__":
    scraper   = TrendScraper(feed_urls=RSS_FEEDS)
    ai_client = OllamaClient()
    affiliate = AffiliateManager()
    generator = ArticleGenerator(ollama_client=ai_client)
    publisher = Publisher()
    db        = DBManager()

    logging.info("打出の小槌システムを起動しました。24時間稼働モードに入ります。")

    while True:
        try:
            run_pipeline(scraper, ai_client, affiliate, generator, publisher, db)
            logging.info(
                f"次の実行まで {config.CHECK_INTERVAL_SECONDS} 秒待機します..."
            )
            time.sleep(config.CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("システムを停止します。")
            break
        except Exception as e:
            logging.error(f"パイプライン実行中にエラーが発生しました: {e}")
            time.sleep(60)
