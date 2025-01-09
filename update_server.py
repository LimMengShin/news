import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

from get_date import get_start_end_date
from newsapi import call_news_api
from urltotext import call_url_to_text_api
from gemini.clean import clean_article

load_dotenv()

gemini_api_keys = os.getenv("GEMINI_API_KEY").split(",")

def split_articles(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

start_date, end_date = get_start_end_date()
articles_list = call_news_api(start_date=start_date, end_date=end_date)
articles_list = list(split_articles(articles_list, len(gemini_api_keys)))

def get_and_clean(articles, gemini_api_key):
    articles_length = len(articles)
    for idx, article in enumerate(articles):
        print(f"ARTICLE {idx + 1}/{articles_length}")
        try:
            article = call_url_to_text_api(article)
        except Exception as e:
            print(f"Error fetching content for {article.get('url')}: {e}")
            continue

        try:
            article["content"] = clean_article(article["content"], gemini_api_key)
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


with ThreadPoolExecutor(max_workers=len(gemini_api_keys)) as executor:
    for idx, articles in enumerate(articles_list):
        executor.submit(get_and_clean, articles, gemini_api_keys[idx])
