"""
analyzer.py  ― Ollama によるニュースセンチメント分析

※ keep_alive=0 で推論後即座に VRAM を解放（RTX 3070 8GB 節約）
※ 金融商品取引法に配慮し「投資判断の推奨」は行わず
   「センチメントの情報提供」として出力する
"""
import json
import logging
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self, host: str, model: str,
                 keep_alive: int = 0, timeout: int = 180):
        self.api_url    = f"{host}/api/generate"
        self.model      = model
        self.keep_alive = keep_alive
        self.timeout    = timeout

    def analyze(self, title: str, summary: str,
                watchlist_names: List[str] = None) -> Dict:
        """
        ニュース記事の投資センチメントを分析する。

        Returns:
            {
                "sentiment":       "positive" | "negative" | "neutral"
                "score":           int  0〜100（市場への影響度）
                "summary":         str  投資家向け50字要約
                "related_tickers": list 関連ティッカー
            }
        """
        names_str = "、".join(watchlist_names) if watchlist_names else "株式市場全般"

        prompt = (
            "あなたは株式市場のニュースアナリストです。\n"
            "以下のニュースを読み、市場センチメントの観点から分析してください。\n"
            "これは情報提供であり、投資推奨ではありません。\n\n"
            f"【関連銘柄候補】{names_str}\n\n"
            f"【タイトル】{title}\n"
            f"【概要】{summary}\n\n"
            "【判定基準】\n"
            "- positive: 企業業績改善・好材料・政策緩和など市場にプラスの内容\n"
            "- negative: 業績悪化・規制強化・リスクオフなど市場にマイナスの内容\n"
            "- neutral:  中立的・市場への影響が限定的な内容\n\n"
            "【影響度スコア基準】\n"
            "- 80〜100: 市場全体・主要銘柄に大きな影響が予想される\n"
            "- 50〜79:  特定セクター・銘柄への影響が予想される\n"
            "- 0〜49:   影響は軽微\n\n"
            "【出力（必ずJSONで返すこと）】\n"
            "{\n"
            '  "sentiment": "positive" | "negative" | "neutral",\n'
            '  "score": 0から100の整数,\n'
            '  "summary": "投資家向け要約（50字以内）",\n'
            '  "related_tickers": ["7203.T", "9984.T"]\n'
            "}"
        )

        payload = {
            "model":      self.model,
            "prompt":     prompt,
            "stream":     False,
            "keep_alive": self.keep_alive,
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            raw = resp.json().get("response", "")
        except requests.exceptions.ConnectionError:
            logger.error("Ollama に接続できません。")
            return self._neutral()
        except Exception as e:
            logger.error(f"Ollama API エラー: {e}")
            return self._neutral()

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            data = json.loads(cleaned)
            return {
                "sentiment":       str(data.get("sentiment", "neutral")),
                "score":           int(data.get("score", 0)),
                "summary":         str(data.get("summary", ""))[:100],
                "related_tickers": data.get("related_tickers", []),
            }
        except Exception as e:
            logger.error(f"JSONパース失敗: {e}\nRaw: {raw[:200]}")
            return self._neutral()

    @staticmethod
    def _neutral() -> Dict:
        return {"sentiment": "neutral", "score": 0,
                "summary": "", "related_tickers": []}
