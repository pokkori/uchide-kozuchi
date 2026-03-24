import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
DB_PATH = "content_data.db"

def get_contents():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, title, url, score, summary,
                       article_title, article_body, tweet_text,
                       published_platforms, created_at
                FROM generated_contents
                ORDER BY score DESC, created_at DESC
            ''')
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"DB Error: {e}")
        return []

@app.route('/')
def index():
    contents = get_contents()
    return render_template('index.html', contents=contents)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
