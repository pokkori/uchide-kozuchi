import feedparser
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrendScraper:
    def __init__(self, feed_urls: List[str]):
        """
        :param feed_urls: RSSフィードのURLリスト
        """
        self.feed_urls = feed_urls

    def fetch_rss_entries(self, max_entries_per_feed: int = 5) -> List[Dict[str, str]]:
        """
        各RSSフィードから最新のトレンド情報を取得する
        """
        all_entries = []
        for url in self.feed_urls:
            logging.info(f"RSSフィードを取得しています: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_entries_per_feed]:
                # 概要からHTMLタグを除去
                summary_text = ""
                if hasattr(entry, 'summary'):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    summary_text = soup.get_text(separator=' ', strip=True)
                
                # タイトルとURL、概要を抽出
                article_data = {
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary_text,
                    "published": getattr(entry, 'published', '')
                }
                all_entries.append(article_data)
                
        return all_entries

    def get_article_text(self, url: str) -> str:
        """
        必要に応じて記事の本文をスクレイピングする
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            # 簡易的に全ての段落テキストを取得
            paragraphs = soup.find_all('p')
            text = " ".join([p.get_text(strip=True) for p in paragraphs])
            return text
        except requests.exceptions.RequestException as e:
            logging.error(f"URLからのテキスト取得に失敗しました {url}: {e}")
            return ""

if __name__ == "__main__":
    # テスト用
    test_urls = ["https://news.yahoo.co.jp/rss/topics/it.xml"]
    scraper = TrendScraper(feed_urls=test_urls)
    entries = scraper.fetch_rss_entries(max_entries_per_feed=2)
    for i, entry in enumerate(entries):
        print(f"\n--- Entry {i+1} ---")
        print(f"Title: {entry['title']}")
        print(f"Summary: {entry['summary'][:100]}...")
