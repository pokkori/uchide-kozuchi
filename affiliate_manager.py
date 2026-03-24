"""
affiliate_manager.py

Amazon PA API 5.0 (AWS SigV4署名) と 楽天市場商品検索API を使って
記事のキーワードに関連する商品を検索し、アフィリエイトリンクを返す。
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Amazon PA API 5.0
# ─────────────────────────────────────────────

class AmazonAffiliateManager:
    SERVICE = "ProductAdvertisingAPI"
    REGION  = "us-east-1"          # PA API は常に us-east-1 で署名
    HOST    = "webservices.amazon.co.jp"
    PATH    = "/paapi5/searchitems"

    def __init__(self):
        self.access_key  = config.AMAZON_ACCESS_KEY
        self.secret_key  = config.AMAZON_SECRET_KEY
        self.partner_tag = config.AMAZON_PARTNER_TAG

    # ── AWS SigV4 署名ヘルパー ──────────────────────────────
    def _sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signing_key(self, date_stamp: str) -> bytes:
        k = self._sign(("AWS4" + self.secret_key).encode("utf-8"), date_stamp)
        k = self._sign(k, self.REGION)
        k = self._sign(k, self.SERVICE)
        k = self._sign(k, "aws4_request")
        return k

    def _build_auth_header(self, payload_str: str, amz_date: str, date_stamp: str,
                           headers: Dict[str, str]) -> str:
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        # 正規ヘッダー（キーをソート）
        sorted_keys = sorted(headers.keys())
        canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted_keys)
        signed_headers = ";".join(sorted_keys)

        canonical_request = "\n".join([
            "POST",
            self.PATH,
            "",
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        credential_scope = f"{date_stamp}/{self.REGION}/{self.SERVICE}/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])

        signing_key = self._get_signing_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"),
                             hashlib.sha256).hexdigest()

        return (
            f"AWS4-HMAC-SHA256 Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

    # ── 商品検索 ────────────────────────────────────────────
    def search_items(self, keyword: str, max_results: int = 3) -> List[Dict]:
        if not config.is_amazon_configured():
            logger.warning("Amazon PA API の認証情報が未設定です。スキップします。")
            return []

        now        = datetime.now(timezone.utc)
        amz_date   = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        payload = {
            "Keywords":    keyword,
            "PartnerTag":  self.partner_tag,
            "PartnerType": "Associates",
            "Marketplace": "www.amazon.co.jp",
            "Resources":   ["ItemInfo.Title", "Offers.Listings.Price"],
            "ItemCount":   max_results,
        }
        payload_str = json.dumps(payload, ensure_ascii=False)

        headers = {
            "content-encoding": "amz-1.0",
            "content-type":     "application/json; charset=utf-8",
            "host":             self.HOST,
            "x-amz-date":      amz_date,
            "x-amz-target":    "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
        }
        headers["authorization"] = self._build_auth_header(
            payload_str, amz_date, date_stamp, headers
        )

        try:
            resp = requests.post(
                f"https://{self.HOST}{self.PATH}",
                data=payload_str.encode("utf-8"),
                headers=headers,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            items = []
            for item in data.get("SearchResult", {}).get("Items", []):
                asin  = item.get("ASIN", "")
                title = (item.get("ItemInfo", {})
                             .get("Title", {})
                             .get("DisplayValue", asin))
                url   = f"https://www.amazon.co.jp/dp/{asin}?tag={self.partner_tag}"
                items.append({"name": title, "affiliate_url": url, "source": "amazon"})
            return items

        except requests.exceptions.HTTPError as e:
            logger.error(f"Amazon PA API HTTPエラー ({e.response.status_code}): "
                         f"{e.response.text[:300]}")
            return []
        except Exception as e:
            logger.error(f"Amazon PA API エラー: {e}")
            return []


# ─────────────────────────────────────────────
#  楽天市場商品検索 API
# ─────────────────────────────────────────────

class RakutenAffiliateManager:
    ENDPOINT = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"

    def __init__(self):
        self.app_id       = config.RAKUTEN_APP_ID
        self.affiliate_id = config.RAKUTEN_AFFILIATE_ID

    def search_items(self, keyword: str, max_results: int = 3) -> List[Dict]:
        if not config.is_rakuten_configured():
            logger.warning("楽天 API の認証情報が未設定です。スキップします。")
            return []

        params: Dict = {
            "applicationId": self.app_id,
            "keyword":       keyword,
            "hits":          max_results,
            "sort":          "-reviewAverage",
            "format":        "json",
        }
        if self.affiliate_id:
            params["affiliateId"] = self.affiliate_id

        try:
            resp = requests.get(self.ENDPOINT, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            items = []
            for wrapper in data.get("Items", []):
                item = wrapper.get("Item", {})
                # affiliateUrl があればそちら、なければ itemUrl を使用
                url = item.get("affiliateUrl") or item.get("itemUrl", "")
                items.append({
                    "name":          item.get("itemName", ""),
                    "affiliate_url": url,
                    "source":        "rakuten",
                })
            return items

        except Exception as e:
            logger.error(f"楽天 API エラー: {e}")
            return []


# ─────────────────────────────────────────────
#  統合クラス
# ─────────────────────────────────────────────

class AffiliateManager:
    """Amazon と 楽天 を束ねて商品検索を行うファサード"""

    def __init__(self):
        self.amazon  = AmazonAffiliateManager()
        self.rakuten = RakutenAffiliateManager()

    def find_products(self, keyword: str, max_per_source: int = 2) -> List[Dict]:
        """
        キーワードで Amazon と 楽天 を検索し、結果を結合して返す。
        最大 max_per_source * 2 件。
        """
        amazon_items  = self.amazon.search_items(keyword, max_per_source)
        rakuten_items = self.rakuten.search_items(keyword, max_per_source)
        products = amazon_items + rakuten_items
        logger.info(
            f"商品検索完了 — Amazon: {len(amazon_items)}件, "
            f"楽天: {len(rakuten_items)}件"
        )
        return products
