import sqlite3

from gemini.lean_bias_tone import get_lean_bias_tone
from gemini.event import get_events
from gemini.event_name import get_event_name
from gemini.ai_article import write_ai_article

events = get_events()

# drop table 'events'
conn = sqlite3.connect('news.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM events;")
conn.commit()
conn.close()

for event in events:
    try:
        thematic_title, short_title = get_event_name(event)
    except Exception as e:
        print(f"Error occurred: {e}")
        continue

    try:
        ai_article = write_ai_article(event)
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
            lean, bias, tone = get_lean_bias_tone(article[5])
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