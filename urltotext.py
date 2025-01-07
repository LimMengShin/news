import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

urltotext_api_key = os.getenv("URLTOTEXT_API_KEY")

# URL to Text API endpoint
URLTOTEXT_URL = "https://urltotext.com/api/v1/urltotext/"

def call_url_to_text_api(article):
    article_url = article.get("url")
    if not article_url or "removed.com" in article_url:
        raise ValueError("Invalid URL")

    # Prepare payload for URL to Text API
    payload = json.dumps({
        "url": article_url,
        "output_format": "html",
        "extract_main_content": True,
        "render_javascript": False
    })
    
    headers = {
        "Authorization": f"Token {urltotext_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(URLTOTEXT_URL, headers=headers, data=payload, timeout=10)  # 10 seconds timeout
        if response.status_code == 200:
            url_data = response.json()
            article["content"] = url_data["data"]["content"]
        else:
            print(f"Failed to fetch content for {article_url}: {response.status_code}, {response.text}")
            raise Exception(f"Failed to fetch content for {article_url}: {response.status_code}, {response.text}")
    except requests.exceptions.Timeout:
        print(f"Timeout occurred for {article_url}. Skipping...")
        raise TimeoutError
    except Exception as e:
        print(f"Error fetching content for {article_url}: {e}")
        raise e

    return article