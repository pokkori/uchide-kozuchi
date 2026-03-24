import os
from dotenv import load_dotenv

load_dotenv()

# ── Twitter / X ───────────────────────────────────────────────
TWITTER_API_KEY            = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET         = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN       = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# ── WordPress ─────────────────────────────────────────────────
WORDPRESS_URL          = os.getenv("WORDPRESS_URL", "")
WORDPRESS_USERNAME     = os.getenv("WORDPRESS_USERNAME", "")
WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")
WORDPRESS_POST_STATUS  = os.getenv("WORDPRESS_POST_STATUS", "draft")

# ── Amazon PA API 5.0 ─────────────────────────────────────────
AMAZON_ACCESS_KEY  = os.getenv("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET_KEY  = os.getenv("AMAZON_SECRET_KEY", "")
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "")

# ── 楽天 ──────────────────────────────────────────────────────
RAKUTEN_APP_ID      = os.getenv("RAKUTEN_APP_ID", "")
RAKUTEN_AFFILIATE_ID = os.getenv("RAKUTEN_AFFILIATE_ID", "")

# ── システム ──────────────────────────────────────────────────
PROFIT_SCORE_THRESHOLD  = int(os.getenv("PROFIT_SCORE_THRESHOLD", "50"))
CHECK_INTERVAL_SECONDS  = int(os.getenv("CHECK_INTERVAL_SECONDS", "600"))

def is_twitter_configured() -> bool:
    return all([TWITTER_API_KEY, TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET])

def is_wordpress_configured() -> bool:
    return all([WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD])

def is_amazon_configured() -> bool:
    return all([AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_PARTNER_TAG])

def is_rakuten_configured() -> bool:
    return bool(RAKUTEN_APP_ID)
