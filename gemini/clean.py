import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def clean_article(article, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    while True:
        try:
            response = model.generate_content(f"""
The following is an unformatted news article in html format. Read it and perform the task that follows.


####################


{article}


####################


Task: Extract only the text of the article


Instruction: extract only the text of the article. remove captions, links to external sites and unrelated content to the article. include headers. do not change any wording of article.""")
            print(response.text[:10])
            return response.text
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e