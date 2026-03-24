"""
collector.py  ― バックグラウンド データ収集ループ

実行: python collector.py
  → 15分ごとに株価・ニュースを取得・分析してDBに保存する
  → Flask ダッシュボード（app.py）とは独立して動作する
"""
import logging
import os
import sys
import time

import yaml

from analyzer import SentimentAnalyzer
from database import InvestmentDB
from fetcher import NewsFetcher, PriceFetcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect(cfg: dict, db: InvestmentDB,
            price_fetcher: PriceFetcher,
            news_fetcher: NewsFetcher,
            analyzer: SentimentAnalyzer):

    watchlist_cfg = cfg["watchlist"]
    col_cfg       = cfg["collector"]
    alert_cfg     = cfg["alerts"]

    # ── 全銘柄の監視名称リストを作成 ──────────────────────────
    all_items = watchlist_cfg.get("stocks", [])
    names     = [item["name"] for item in all_items]

    # ══════════════════════════════════════════════════════════
    #  Step 1: 株価スナップショット取得
    #  ※ yfinance はネットワーク IO のみ、VRAM は使用しない
    # ══════════════════════════════════════════════════════════
    logger.info("─── Step 1: 株価を取得中 ───")
    prices = price_fetcher.fetch_all(all_items)
    for p in prices:
        db.save_price(**p)
        chg = p["change_pct"]
        flag = ""
        if abs(chg) >= alert_cfg["price_change_threshold"]:
            flag = " ⚠️ アラート"
        logger.info(
            f"  {p['name']:12s}  ¥{p['price']:>10,.0f}  "
            f"({chg:+.2f}%){flag}"
        )

    # ══════════════════════════════════════════════════════════
    #  Step 2: ニュース取得
    # ══════════════════════════════════════════════════════════
    logger.info("─── Step 2: ニュースを取得中 ───")
    articles = news_fetcher.fetch(max_per_feed=col_cfg["max_news_per_feed"])
    new_count = sum(1 for a in articles if not db.is_url_analyzed(a["url"]))
    logger.info(f"  取得: {len(articles)} 件 / 未分析: {new_count} 件")

    # ══════════════════════════════════════════════════════════
    #  Step 3: 未分析ニュースを Ollama で分析
    #  ※ keep_alive=0 で各推論後に VRAM を解放
    # ══════════════════════════════════════════════════════════
    logger.info("─── Step 3: センチメント分析中（Ollama） ───")
    analyzed = 0
    for article in articles:
        if db.is_url_analyzed(article["url"]):
            continue

        result = analyzer.analyze(
            title=article["title"],
            summary=article["summary"],
            watchlist_names=names,
        )

        if result["score"] >= col_cfg["min_sentiment_score"]:
            db.save_news(
                title=article["title"],
                url=article["url"],
                sentiment=result["sentiment"],
                score=result["score"],
                summary=result["summary"],
                related_tickers=result["related_tickers"],
                published=article["published"],
            )
            icon = {"positive": "🟢", "negative": "🔴"}.get(
                result["sentiment"], "⚪"
            )
            logger.info(
                f"  {icon} [{result['score']:3d}] {article['title'][:40]}"
            )
        else:
            # スコアが低くてもURLは記録して再処理を防ぐ
            db.save_news(
                title=article["title"],
                url=article["url"],
                sentiment=result["sentiment"],
                score=result["score"],
                summary=result["summary"],
                related_tickers=result["related_tickers"],
                published=article["published"],
            )
        analyzed += 1

    logger.info(f"  分析完了: {analyzed} 件")


def main():
    cfg = load_config()
    os.makedirs(os.path.dirname(cfg["database"]["path"]), exist_ok=True)

    db            = InvestmentDB(cfg["database"]["path"])
    price_fetcher = PriceFetcher()
    news_fetcher  = NewsFetcher(cfg["news_feeds"])
    analyzer      = SentimentAnalyzer(
        host=cfg["ollama"]["host"],
        model=cfg["ollama"]["model"],
        keep_alive=cfg["ollama"]["keep_alive"],
        timeout=cfg["ollama"]["timeout"],
    )

    interval = cfg["collector"]["interval_seconds"]
    logger.info(f"データ収集を開始します（{interval}秒ごと）")

    while True:
        try:
            collect(cfg, db, price_fetcher, news_fetcher, analyzer)
            logger.info(f"次の収集まで {interval} 秒待機します...")
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("停止しました。")
            break
        except Exception as e:
            logger.error(f"収集エラー: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
