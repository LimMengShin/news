import sqlite3

from get_date import get_start_end_date
from newsapi import call_news_api
from urltotext import call_url_to_text_api
from gemini.clean import clean_article
from gemini.lean_bias_tone import get_lean_bias_tone
from gemini.event import get_events
from gemini.event_name import get_event_name
from gemini.ai_article import write_ai_article

start_date, end_date = get_start_end_date()
articles = call_news_api(start_date=start_date, end_date=end_date)

articles_length = len(articles)

for idx, article in enumerate(articles):
    print(f"ARTICLE {idx + 1}/{articles_length}")
    try:
        article = call_url_to_text_api(article)
    except Exception as e:
        print(f"Error fetching content for {article.get('url')}: {e}")
        continue

    try:
        article["content"] = clean_article(article["content"])
    except Exception as e:
        print(f"Error cleaning content for {article.get('url')}: {e}")
        continue


    # insert to SQLite database
    connection = sqlite3.connect("news.db")
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO news_articles (date, news_source, news_title, url, content, image_url, news_source_name)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    values = (article["publishedAt"], article["source"]["id"], article["title"], article["url"], article["content"], article["urlToImage"], article["source"]["name"])

    if article["urlToImage"] is None:
        insert_query = """
        INSERT INTO news_articles (date, news_source, news_title, url, content, news_source_name)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        values = (article["publishedAt"], article["source"]["id"], article["title"], article["url"], article["content"], article["source"]["name"])


    cursor.execute(insert_query, values)
    connection.commit()
    connection.close()


# Get events
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