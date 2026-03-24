"""
app.py  ― Flask 投資ダッシュボード

実行: python app.py
  → http://127.0.0.1:5001 でダッシュボードを表示
  → collector.py と並行して動かすこと
"""
import os
import yaml
from flask import Flask, jsonify, render_template

from database import InvestmentDB

app = Flask(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


cfg = load_config()
db  = InvestmentDB(cfg["database"]["path"])


@app.route("/")
def index():
    prices     = db.get_latest_prices()
    news       = db.get_recent_news(limit=60)
    alert_news = db.get_alert_news(cfg["alerts"]["sentiment_score_threshold"])
    return render_template(
        "dashboard.html",
        prices=prices,
        news=news,
        alert_news=alert_news,
        watchlist=cfg["watchlist"],
    )


@app.route("/api/prices")
def api_prices():
    return jsonify(db.get_latest_prices())


@app.route("/api/news")
def api_news():
    return jsonify(db.get_recent_news(limit=100))


if __name__ == "__main__":
    os.makedirs(os.path.dirname(cfg["database"]["path"]), exist_ok=True)
    dash_cfg = cfg["dashboard"]
    app.run(
        host=dash_cfg["host"],
        port=dash_cfg["port"],
        debug=dash_cfg["debug"],
    )
