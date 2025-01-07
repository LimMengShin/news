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

def write_ai_article(event):
    article_contents = ""
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
        article_contents += article[5] + "\n\n\n\n-------------------\n\n\n\n"
    while True:
        try:
            response = model.generate_content(f"""
The following is a list of articles of a collection of news articles around a particular event. Read them and perform the task that follows. Respond with a JSON object of a key-value pair.


####################


{article_contents}


####################


Task: Write an unbiased and impartial article.


Instruction:

Analyze the news articles about a specific topic that may or may not include biased perspectives. Using these sources, please write an unbiased and impartial news article. Ensure the article:  

1. **Provides Only Facts**: Summarize the information in a factual manner without including personal opinions, editorializing, or emotionally charged language.  

2. **Acknowledges Both Sides**: Present both sides (or all perspectives) of the issue, giving balanced coverage to each without favoring one side over another.  

3. **Sources Information Fairly**: Clearly attribute facts to their respective sources or broadly reference credible sources without injecting interpretation.  

4. **Neutral Language**: Use neutral and formal language throughout the article to ensure it maintains professionalism and impartiality.  

5. **Avoids Assumptions**: Do not make any assumptions or draw conclusions beyond what is explicitly stated in the provided information.  

**Tone and Style:**  
- Objective, factual, and formal.  
- Avoiding adjectives or phrases that imply judgment or favorability.  

If you need additional clarification about the sources or have conflicting information, please highlight it in the article and explain the context without forming conclusions.  


Key: "ai_article"
Value: The article.


Do not return anything except the JSON object of key-value pair as output.""")
            print(response.text)
            try:
                cleaned_response = re.sub(r'^```json|```$', '', response.text, flags=re.MULTILINE).strip()
                ai_article = json.loads(cleaned_response)["ai_article"]
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e
            return ai_article
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e
