import json
import logging
from typing import Dict, List

from ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class ArticleGenerator:
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client

    def generate(self, title: str, summary: str, products: List[Dict]) -> Dict[str, str]:
        """
        トレンド情報と関連商品からアフィリエイト記事・Twitter文を生成する。

        Returns:
            {
                "article_title": str,   # SEOタイトル
                "article_body":  str,   # 1000〜1500字の記事本文
                "tweet":         str,   # 280字以内のTwitter投稿文
            }
        """
        product_section = self._build_product_section(products)

        prompt = (
            "あなたはSEOに強いプロのアフィリエイトブロガーです。\n"
            "以下のトレンド情報と関連商品を元に、読者を引き込み商品購入につながる\n"
            "日本語のアフィリエイト記事を作成してください。\n\n"
            "【記事の要件】\n"
            "- 文字数: 1000〜1500字\n"
            "- 構成: ①導入（読者の悩み・興味を刺激）→ ②詳細解説 → ③商品紹介 → ④まとめ\n"
            "- 商品紹介セクションでは各商品名とURLをそのまま本文中に自然に挿入すること\n"
            "- 読者目線の親しみやすい文体で書くこと\n"
            "- SEOを意識し、タイトルにはメインキーワードを含めること\n\n"
            "【Twitterの要件】\n"
            "- 280字以内\n"
            "- 記事の魅力を端的に伝え、クリックしたくなる文章\n\n"
            f"【トレンドタイトル】\n{title}\n\n"
            f"【概要】\n{summary}\n"
            f"{product_section}\n"
            "【出力フォーマット（必ずJSONで返すこと。Markdownコードブロック不要）】\n"
            "{\n"
            "  \"article_title\": \"SEOを意識したタイトル\",\n"
            "  \"article_body\": \"記事本文（1000〜1500字）\",\n"
            "  \"tweet\": \"Twitter投稿文（280字以内）\"\n"
            "}"
        )

        logger.info("Ollamaで記事本文を生成中...")
        raw = self.client.generate(prompt)

        if not raw:
            logger.warning("記事生成レスポンスが空でした。フォールバック値を使用します。")
            return self._fallback(title, summary)

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            result = json.loads(cleaned)
            return {
                "article_title": str(result.get("article_title", title)),
                "article_body":  str(result.get("article_body", summary)),
                "tweet":         str(result.get("tweet", summary[:280])),
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"記事生成JSONパース失敗: {e}")
            return self._fallback(title, raw)

    def _build_product_section(self, products: List[Dict]) -> str:
        if not products:
            return ""
        lines = ["【関連商品（アフィリエイトリンク付き）】"]
        for p in products:
            source = p.get("source", "")
            label = "[Amazon]" if source == "amazon" else "[楽天]"
            lines.append(f"- {label} {p['name']}: {p['affiliate_url']}")
        return "\n".join(lines) + "\n\n"

    def _fallback(self, title: str, body: str) -> Dict[str, str]:
        return {
            "article_title": title,
            "article_body":  body,
            "tweet":         body[:280],
        }
