import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import sqlite3
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def get_event_name(event):
    article_titles = ""
    for element in event:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()

        select_query = """
        SELECT * FROM news_articles
        WHERE id = ?;
        """
        values = (element,)
        cursor.execute(select_query, values)
        article = cursor.fetchone()
        conn.close()
        article_titles += article[3] + "\n"
    while True:
        try:
            response = model.generate_content(f"""
The following is a list of titles of a collection of news articles around a particular event. Read them and perform the task that follows. Respond with a JSON object of key-value pairs.


####################


{article_titles}


####################


Task: Summarize the titles.


1. Instruction: Analyze the titles and produce a good thematic title that best summarizes the event.
Key: "theme"
Value: The thematic title.


2. Instruction: Analyze the titles and produce a shorter title that is not longer than 4 to 5 words.
Key: "theme_short"
Value: The shorter title.


Do not return anything except the JSON object of key-value pairs as output.""")
            print(response.text)
            try:
                cleaned_response = re.sub(r'^```json|```$', '', response.text, flags=re.MULTILINE).strip()
                theme = json.loads(cleaned_response)["theme"]
                theme_short = json.loads(cleaned_response)["theme_short"]
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e
            return theme, theme_short
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e