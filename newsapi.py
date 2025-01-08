import requests
from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

news_api_key = os.getenv("NEWS_API_KEY")

# News API endpoint
NEWS_API_URL = "https://newsapi.org/v2/everything"


def call_news_api(start_date, end_date):
    articles = []
    while start_date <= end_date:
        page = 1
        while True:
            news_params = {
                "sources": "abc-news,associated-press,bloomberg,business-insider,the-huffington-post,msnbc,cbs-news,cnn,politico,time,the-american-conservative,breitbart-news,fox-news,national-review,the-washington-times",
                "page": page,
                "from": start_date,
                "to": end_date,
                "sortBy": "popularity",
                "language": "en",
                "apiKey": news_api_key
            }
            
            # Fetch articles from News API
            response = requests.get(NEWS_API_URL, params=news_params)
            if response.status_code != 200:
                break
            
            data = response.json()
            articles.extend(data.get("articles", []))
            
            # Stop if no more pages
            if len(data.get("articles", [])) < 100:
                break
            
            page += 1
        start_date += timedelta(days=1)
    
    return articles

