"""
fetcher.py  ― 株価・ニュースデータ取得
  - 株価: yfinance（無料・無制限）
  - ニュース: RSS フィード
"""
import logging
from typing import Dict, List, Optional

import feedparser
import requests
import yfinance as yf
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ── 株価取得 ─────────────────────────────────────────────────

class PriceFetcher:
    def fetch(self, ticker: str, name: str, asset_type: str = "stock") -> Optional[Dict]:
        """
        yfinance で現在値・前日比・出来高を取得する。
        日本株: "7203.T"  米国株: "AAPL"  仮想通貨: "BTC-JPY"
        """
        try:
            tk   = yf.Ticker(ticker)
            hist = tk.history(period="5d")   # 5日分あれば前日比が確実に取れる
            if hist.empty:
                logger.warning(f"価格データが取得できませんでした: {ticker}")
                return None

            current  = float(hist["Close"].iloc[-1])
            prev     = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else current
            chg_pct  = (current - prev) / prev * 100 if prev != 0 else 0.0
            volume   = int(hist["Volume"].iloc[-1])

            return {
                "ticker":     ticker,
                "name":       name,
                "price":      round(current, 2),
                "change_pct": round(chg_pct, 2),
                "volume":     volume,
                "asset_type": asset_type,
            }
        except Exception as e:
            logger.error(f"株価取得エラー [{ticker}]: {e}")
            return None

    def fetch_all(self, watchlist: List[Dict]) -> List[Dict]:
        results = []
        for item in watchlist:
            data = self.fetch(
                ticker=item["ticker"],
                name=item.get("name", item["ticker"]),
                asset_type=item.get("asset_type", "stock"),
            )
            if data:
                results.append(data)
        return results


# ── ニュース取得 ──────────────────────────────────────────────

class NewsFetcher:
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls

    def fetch(self, max_per_feed: int = 10) -> List[Dict]:
        articles = []
        for url in self.feed_urls:
            try:
                feed = feedparser.parse(url)
                logger.info(f"RSS取得: {url} ({len(feed.entries)} 件)")
                for entry in feed.entries[:max_per_feed]:
                    summary = ""
                    if hasattr(entry, "summary"):
                        summary = BeautifulSoup(
                            entry.summary, "html.parser"
                        ).get_text(separator=" ", strip=True)

                    articles.append({
                        "title":     getattr(entry, "title",     ""),
                        "url":       getattr(entry, "link",      ""),
                        "summary":   summary,
                        "published": getattr(entry, "published", ""),
                    })
            except Exception as e:
                logger.error(f"ニュース取得エラー [{url}]: {e}")
        return articles
