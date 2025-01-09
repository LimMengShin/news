import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import random
from random import randint

from gemini.lean_bias_tone import get_lean_bias_tone
from gemini.event import get_events
from gemini.event_name import get_event_name
from gemini.ai_article import write_ai_article

load_dotenv()

gemini_api_keys = os.getenv("GEMINI_API_KEY").split(",")
gemini_api_key = gemini_api_keys[randint(0, len(gemini_api_keys)-1)]

def split_articles(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

# Get events
events_list = get_events(gemini_api_key)
print(len(events_list))
random.shuffle(events_list)
events_list = list(split_articles(events_list, len(gemini_api_keys)))

# drop table 'events'
conn = sqlite3.connect('news.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM events;")
conn.commit()
conn.close()

def ai_title_article(events, gemini_api_key):
    for event in events:
        try:
            thematic_title, short_title = get_event_name(event, gemini_api_key)
        except Exception as e:
            print(f"Error occurred: {e}")
            continue

        try:
            ai_article = write_ai_article(event, gemini_api_key)
        except Exception as e:
            print(f"Error occurred: {e}")
            continue

        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO events (thematic_title, short_title, ai_article, article_ids)
        VALUES (?, ?, ?, ?);
        """
        event_data = (
            thematic_title,
            short_title,
            ai_article,
            ",".join([str(x) for x in event])
        )
        cursor.execute(insert_query, event_data)
        conn.commit()
        conn.close()
        
        for id_no in event:
            conn = sqlite3.connect('news.db')
            cursor = conn.cursor()
            select_query = """
            SELECT * FROM news_articles
            WHERE id = ?;
            """
            article = cursor.execute(select_query, (id_no,)).fetchone()
            
            lean = bias = tone = None
            try:
                lean, bias, tone = get_lean_bias_tone(article[5], gemini_api_key)
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

            conn = sqlite3.connect('news.db')
            cursor = conn.cursor()

            update_query = """
            UPDATE news_articles
            SET lean = ?, bias = ?, tone = ?
            WHERE id = ?;
            """
            cursor.execute(update_query, (tone, lean, bias, id_no))
            conn.commit()
            conn.close()


with ThreadPoolExecutor(max_workers=len(gemini_api_keys)) as executor:
    for idx, events in enumerate(events_list):
        executor.submit(ai_title_article, events, gemini_api_keys[idx])
