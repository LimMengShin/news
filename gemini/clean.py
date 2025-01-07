import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash-exp")


def clean_article(article):
    while True:
        try:
            response = model.generate_content(f"""
The following is an unformatted news article in html format. Read it and perform the task that follows.


####################


{article}


####################


Task: Extract only the text of the article


Instruction: extract only the text of the article. remove captions, links to external sites and unrelated content to the article. include headers. do not change any wording of article.""")
            print(response.text)
            return response.text
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            raise e