from flask import Flask, render_template, g, request, jsonify
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import sqlite3
import time
from dotenv import load_dotenv
import os
from random import randint

app = Flask(__name__)

database = 'news.db'

load_dotenv()

gemini_api_keys = os.getenv("GEMINI_API_KEY").split(",")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    events = query_db("SELECT id, thematic_title, ai_article, article_ids FROM events ORDER BY LENGTH(article_ids) - LENGTH(REPLACE(article_ids, ',', '')) DESC")
    image_urls = []
    for event in events:
        article_ids = [int(id.strip()) for id in event['article_ids'].split(',')]
        placeholders = ','.join('?' for _ in article_ids)
        articles = query_db(f"SELECT * FROM news_articles WHERE id IN ({placeholders})", article_ids)
        image_urls.append(articles[-1]['image_url'])
    return render_template('index.html', events=events, image_urls=image_urls)

@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = query_db("SELECT id, thematic_title, ai_article, article_ids FROM events WHERE id = ?", [event_id], one=True)
    if event:
        article_ids = [int(id.strip()) for id in event['article_ids'].split(',')]
        placeholders = ','.join('?' for _ in article_ids)
        articles = query_db(f"SELECT * FROM news_articles WHERE id IN ({placeholders})", article_ids)
        
        # Convert each row to a dictionary and handle None values
        articles = [
            {
                **dict(article),
                'lean': article['lean'] or 0,
                'bias': -(article['bias'] or 0)+5,
                'tone': (article['tone'] or 0)+5,
            }
            for article in articles
        ]
        
        image_urls = []
        for article in articles:
            image_urls.append(article['image_url'])
        ai_article = event["ai_article"].replace("\n", "<br />")
    else:
        articles = []
        image_urls = []
        ai_article = ""
    return render_template('event.html', event=event, articles=articles, ai_article=ai_article, image_urls=image_urls)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    if query:
        results = query_db(
            "SELECT id, thematic_title FROM events WHERE LOWER(thematic_title) LIKE ?",
            [f"%{query}%"]
        )
        return jsonify([{"id": r["id"], "title": r["thematic_title"]} for r in results])
    return jsonify([])

@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    data = request.get_json()
    try:
        event_id = int(data.get('event_id'))
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid input'})
    highlighted_text = data.get('highlighted_text')
    question = data.get('question')

    if not question:
        return jsonify({'success': False, 'error': 'Invalid input'})
    event = query_db("SELECT ai_article FROM events WHERE id = ?", [event_id], one=True)
    if highlighted_text:
        highlighted_query = f"""
The following is a highlighted portion of the news article.

####################


{highlighted_text}


####################
"""
        highlighted_prompt = " the highlighted portion of"
    else:
        highlighted_query = ""
        highlighted_prompt = ""
    query = f"""
The following is a news article about an event.

####################


{event["ai_article"]}


####################


{highlighted_query}


The following is a question by a user regarding{highlighted_prompt} the news article.

####################


{question}


####################


Read the provided news article and respond to the user's query. You can refer to the article or search online. Answer in a fun helpful and kind way. Answer in a similar manner as the user. Answer directly without markdown and in one paragraph only.
"""
    
    gemini_api_key = gemini_api_keys[randint(0, len(gemini_api_keys)-1)]
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    while True:  # Keep retrying until successful
        try:
            response = model.generate_content(query)
            print(response.text)
            return jsonify({'success': True, 'answer': response.text})
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            return jsonify({'success': False, 'error': 'Failed to contact Gemini AI'})


if __name__ == '__main__':
    app.run(debug=True)

def create_app():
    return app