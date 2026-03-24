import json
import logging
import requests
from typing import Dict, Any, Optional

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3:8b"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/generate"

    def generate(self, prompt: str, keep_alive: int = 0) -> Optional[str]:
        """
        OllamaのAPIを呼び出してテキストを生成する。
        keep_alive=0により、生成完了後にVRAMからモデルを即座に解放する(RTX 3070のVRAM節約のため)。
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": keep_alive
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=180)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama API Error: {e}")
            return None

    def evaluate_profitability(self, text: str) -> Dict[str, Any]:
        """
        与えられたテキストの収益性(0-100)と要約を算出する。
        """
        prompt = (
            "あなたは優秀なアフィリエイトマーケター兼コンテンツアナリストです。\n"
            "以下の記事の概要を読み、そこからアフィリエイトやSNSでの収益化のポテンシャルを0から100のスコアで評価してください。\n"
            "また、その記事を元にしたSNS投稿用の簡潔な要約（魅力的な文章）を作成してください。\n\n"
            "【出力フォーマット（必ずJSON形式で、以下のキーを含めて返してください。Markdownのコードブロックは不要です。）】\n"
            "{\n"
            "  \"score\": 85,\n"
            "  \"summary\": \"ここにSNS投稿用の魅力的な文章\"\n"
            "}\n\n"
            f"【対象記事】\n{text}"
        )
        
        logging.info("Ollamaに評価リクエストを送信しています...")
        response_text = self.generate(prompt)
        
        if not response_text:
            return {"score": 0, "summary": "評価に失敗しました。"}
            
        # 簡易的にJSONパースを試みる
        try:
            # Markdownのコードブロックが含まれる場合を取り除く
            cleaned_text = response_text.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                
            result_json = json.loads(cleaned_text)
            
            # 結果の整形
            score = int(result_json.get("score", 0))
            summary = str(result_json.get("summary", ""))
            return {
                "score": score,
                "summary": summary
            }
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"レスポンスのJSONパースに失敗しました: {e}\nRaw response: {response_text}")
            return {"score": 0, "summary": response_text.strip()}

if __name__ == "__main__":
    # 簡単なテスト用コード (手動実行時に確認可能)
    client = OllamaClient()
    test_article = "最新のAIツール「Antigravity」がリリースされました。プログラミングを自動化し、作業効率を劇的に向上させる革新的なツールとして注目を集めています。"
    print(f"テスト記事: {test_article}")
    result = client.evaluate_profitability(test_article)
    print("\n【評価結果】")
    try:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except UnicodeEncodeError:
        print(json.dumps(result, indent=2, ensure_ascii=False).encode('utf-8', 'replace').decode('utf-8'))
