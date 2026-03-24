"""
text_generator.py

Ollama (llama3:8b) を呼び出して YouTube ショート用スクリプトを生成する。
推論後は keep_alive=0 で即座に VRAM を解放する（RTX 3070 8GB 節約）。
"""

import json
import logging
import sys
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class YouTubeScriptGenerator:
    def __init__(self, host: str, model: str, keep_alive: int = 0, timeout: int = 180):
        self.host       = host
        self.model      = model
        self.keep_alive = keep_alive
        self.timeout    = timeout
        self.api_url    = f"{host}/api/generate"

    def _call_ollama(self, prompt: str) -> Optional[str]:
        payload = {
            "model":      self.model,
            "prompt":     prompt,
            "stream":     False,
            "keep_alive": self.keep_alive,
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.exceptions.ConnectionError:
            logger.error("Ollama に接続できません。`ollama serve` が起動しているか確認してください。")
            return None
        except Exception as e:
            logger.error(f"Ollama API エラー: {e}")
            return None

    def generate_script(self, genre: str = "驚きの雑学",
                        max_chars: int = 300) -> Optional[dict]:
        """
        YouTube ショート用スクリプトを生成する。

        Returns:
            {
                "title":    str,        # 動画タイトル（30字以内）
                "script":   str,        # ナレーション原稿（〜300字）
                "keywords": list[str],  # 関連キーワード
                "subtitles": list[str], # 字幕用に分割した文のリスト
            }
        """
        prompt = (
            f"あなたはYouTubeショート動画のプロのスクリプターです。\n"
            f"視聴者が思わず「へえ！」と言いたくなる「{genre}」を1つ考えて、\n"
            f"YouTubeショート（60秒以内）のナレーション原稿を作成してください。\n\n"
            f"【要件】\n"
            f"- 冒頭の一文で視聴者の興味を強く引くこと\n"
            f"- 全体で200〜{max_chars}字程度（読み上げ時間：約45〜60秒）\n"
            f"- 簡単な言葉・テンポよい文体で書くこと\n"
            f"- 文末は「。」で終わる文に分割して書くこと\n\n"
            f"【出力フォーマット（必ずJSONで返すこと）】\n"
            "{\n"
            '  "title": "動画タイトル（30字以内）",\n'
            '  "script": "ナレーション原稿の全文",\n'
            '  "keywords": ["キーワード1", "キーワード2", "キーワード3"],\n'
            '  "subtitles": ["文1。", "文2。", "文3。"]\n'
            "}"
        )

        logger.info(f"Ollama でスクリプトを生成中（ジャンル: {genre}）...")
        raw = self._call_ollama(prompt)

        if not raw:
            return None

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()

            result = json.loads(cleaned)

            # subtitles が無い場合は script を句点で分割して生成
            if "subtitles" not in result or not result["subtitles"]:
                script = result.get("script", "")
                result["subtitles"] = [s.strip() + "。"
                                       for s in script.split("。") if s.strip()]

            logger.info(f"スクリプト生成完了: 「{result.get('title', '')}」")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSONパース失敗: {e}")
            # フォールバック：生テキストをそのまま使う
            sentences = [s.strip() + "。" for s in raw.split("。") if s.strip()]
            return {
                "title":     f"{genre}の話",
                "script":    raw.strip()[:max_chars],
                "keywords":  [genre],
                "subtitles": sentences[:10],
            }
