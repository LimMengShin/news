import newspaper

def call_url_to_text_api(article):
    article_url = article.get("url")
    if not article_url or "removed.com" in article_url:
        raise ValueError("Invalid URL")
    try:
        text = newspaper.article(article_url).text
        if text:
            article["content"] = text
        else:
            raise ValueError("No content found")
    except Exception as e:
        raise e
    return article