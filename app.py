from flask import Flask, render_template, g, request, jsonify, redirect
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import sqlite3
import time
from dotenv import load_dotenv
import os
from random import randint
import newspaper

app = Flask(__name__)

database = "news.db"

load_dotenv()

gemini_api_keys = os.getenv("GEMINI_API_KEY").split(",")

def get_db():
    db = getattr(g, "_database", None)
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
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    events = query_db("SELECT id, thematic_title, ai_article, article_ids FROM events ORDER BY LENGTH(article_ids) - LENGTH(REPLACE(article_ids, ',', '')) DESC")
    image_urls = []
    for event in events:
        article_ids = [int(id.strip()) for id in event["article_ids"].split(",")]
        placeholders = ",".join("?" for _ in article_ids)
        articles = query_db(f"SELECT * FROM news_articles WHERE id IN ({placeholders})", article_ids)
        image_urls.append(articles[-1]["image_url"])
    return render_template("index.html", events=events, image_urls=image_urls)

@app.route("/event/<int:event_id>")
def event_details(event_id):
    event = query_db("SELECT id, thematic_title, ai_article, article_ids FROM events WHERE id = ?", [event_id], one=True)
    if event:
        article_ids = [int(id.strip()) for id in event["article_ids"].split(",")]
        placeholders = ",".join("?" for _ in article_ids)
        articles = query_db(f"SELECT * FROM news_articles WHERE id IN ({placeholders})", article_ids)
        
        # Convert each row to a dictionary and handle None values
        articles = [
            {
                **dict(article),
                "lean": article["lean"] or 0,
                "bias": -(article["bias"] or 0)+5,
                "tone": (article["tone"] or 0)+5,
            }
            for article in articles
        ]
        
        image_urls = []
        for article in articles:
            image_urls.append(article["image_url"])
        ai_article = event["ai_article"].replace("\n", "<br />")
    else:
        articles = []
        image_urls = []
        ai_article = ""
    return render_template("event.html", event=event, articles=articles, ai_article=ai_article, image_urls=image_urls)

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").lower()
    if query:
        results = query_db(
            "SELECT id, thematic_title FROM events WHERE LOWER(thematic_title) LIKE ?",
            [f"%{query}%"]
        )
        return jsonify([{"id": r["id"], "title": r["thematic_title"]} for r in results])
    return jsonify([])

article_dict = {"title": "Enter URL above to see your article here!",
                "image": "https://upload.wikimedia.org/wikipedia/commons/4/48/BLANK_ICON.png",
                "text": "Nothing here now..."}

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST":
        error = False
        url = request.form.get("url")
        option = request.form.get("options")
        if url and option in ["bias", "lean", "tone", "simplify"]:
            try:
                article = newspaper.article(url)
                title = article.title
                text = article.text
                image = article.top_image
                if title:
                    article_dict["title"] = title
                else:
                    article_dict["title"] = "Article title not found"
                if image:
                    article_dict["image"] = image
                else:
                    article_dict["image"] = "https://upload.wikimedia.org/wikipedia/commons/d/d1/Image_not_available.png"
                if text:
                    article_dict["text"] = text
                    print(text)
                else:
                    article_dict["text"] = "Article content not found. Try again perhaps?"
                    error = True
            except:
                error = True
        else:
            article_dict["title"] = "Invalid URL and/or conversion option"
            error = True
        if not error:
            option_idx = ["bias", "lean", "tone", "simplify"].index(option)
            prompts = ["""
Task: Rewrite the above news article to be unbiased and impartial.


Instruction:

Analyze the news article that may or may not include biased perspectives. Rewrite the above news article to be unbiased and impartial.
Ensure the article provides only facts, acknowledges both sides, uses neutral language, and avoids assumptions.
""",
"""
Task: Rewrite the above news article to have the opposite political leaning.


Instruction:

Analyze the news article that is of a certain political leaning in the context of U.S. politics. Rewrite it such that it has the opposite political lean.
For example, an article that is conservative should be rewritten such that it becomes liberal.
""",
"""
Task: Rewrite the above news article to have the opposite tone.


Instruction:

Analyze the news article that is of a certain tone. Rewrite it such that it has the opposite tone.
For example, an article that has a positive tone should be rewritten such that it has a negative tone.
""",
"""
Task: Simplify the above news article.


Instruction:

Analyze the news article that and simplify it such that it is more understandable.
It should use simpler words and vocabulary such that a 9th grader can understand it.
"""]
            prompt = prompts[option_idx]
            prompt = f"""
The following is a news article. Read it carefully and perform the task that follows.

---

Article:

{article_dict["text"]}

---


""" + prompt + """


Return only the rewrritten article in markdown format with paragragh breaks with no other text.
"""
            gemini_api_key = gemini_api_keys[randint(0, len(gemini_api_keys)-1)]
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            while True:  # Keep retrying until successful
                try:
                    response = model.generate_content(prompt)
                    print(response.text)
                    article_dict["text"] = response.text
                    break
                except ResourceExhausted:
                    print("Quota exhausted. Waiting for 5 seconds before retrying...")
                    time.sleep(5)
                except Exception as e:
                    print(f"Error occurred: {e}")
                    break
        return redirect("/convert")
    return render_template("convert.html", article_dict=article_dict)

@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    data = request.get_json()
    print(data)
    if "event_id" in data:
        try:
            event_id = int(data.get("event_id"))
        except ValueError:
            return jsonify({"success": False, "error": "Invalid input"})
        event = query_db("SELECT ai_article FROM events WHERE id = ?", [event_id], one=True)
        news_article_content = event["ai_article"]
    else:
        news_article_content = article_dict["text"]
    
    highlighted_text = data.get("highlighted_text")
    question = data.get("question")

    if not question:
        return jsonify({"success": False, "error": "Invalid input"})
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


{news_article_content}


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
            return jsonify({"success": True, "answer": response.text})
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            return jsonify({"success": False, "error": "Failed to contact Gemini AI"})


if __name__ == "__main__":
    app.run(debug=True)

def create_app():
    return app