import sqlite3
from datetime import datetime

from newsapi import call_news_api
from urltotext import call_url_to_text_api
from gemini.clean import clean_article

yesterday = datetime.now().day-1
articles = call_news_api(date=f"2025-01-{yesterday:02d}")

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