import re
import json
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def get_lean_bias_tone(article, gemini_api_key):
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    tries = 0
    while True:
        try:
            response = model.generate_content(f"""
The following is a news article. Read it carefully and perform the tasks that follow. Respond strictly in the form of a JSON object containing the requested key-value pairs.

---

### Article:

{article}

---

### Task 1: Political Leaning Evaluation
**Instruction:** Analyze the article's political leaning in the context of U.S. politics. Assess whether the article leans toward the Democratic party, Republican party, or remains neutral. Use a scoring system to evaluate its leaning across the following four criteria, with reasoning for each score.

#### Scoring Scale:
- **-5**: Strongly favors the Republican party.
- **-1 to -4**: Leans Republican.
- **0**: Neutral or balanced.
- **1 to 4**: Leans Democrat.
- **5**: Strongly favors the Democratic party.

#### Evaluation Criteria:
1. **Language Alignment**  
   - Does the article’s language reflect values or terminology commonly associated with one political party?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Describe specific language used and its alignment with a party.

2. **Policy Support**  
   - Does the article highlight or endorse policies traditionally linked to a specific party?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Explain which party’s policies are supported and how they are presented.

3. **Political Figures Mentioned**  
   - Are political figures from a party prominently featured? How are they portrayed?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Detail the portrayal of political figures and any noticeable bias.

4. **Tone and Framing**  
   - Is the tone of the article favorable to one party?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Describe how the tone supports or criticizes a party.

#### Output:  
- **"criteria"**: Dictionary of individual scores and explanations for the four criteria.  
- **"overallLeanScore"**: Integer average of the scores, rounded to the nearest whole number. Include reasoning for the overall score.  

---

### Task 2: Bias Evaluation
**Instruction:** Assess the article’s bias using the following criteria. Assign a score from -5 (extremely biased) to 5 (completely neutral) for each. Provide explanations for each score and calculate the overall bias score.

#### Criteria:
1. **Language Neutrality**  
   - Is the language formal, avoiding emotionally charged terms?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Explain whether the language is neutral or biased.

2. **Balanced Representation**  
   - Are different perspectives on the issue fairly represented?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Describe the balance (or lack thereof) in presenting viewpoints.

3. **Fact vs. Opinion**  
   - Does the article rely on verified facts, or does it mix in opinions and speculation?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Explain any reliance on opinions or unverified claims.

4. **Source Attribution and Context**  
   - Are facts attributed to credible sources, avoiding assumptions or overgeneralizations?  
   - **Score Range:** -5 to 5  
   - **Explanation:** Assess the quality of sourcing and attribution.

#### Output:
- **"criteria"**: Dictionary of scores and explanations for each criterion.  
- **"overallBiasScore"**: Float average of the scores, rounded to two decimal places.  
- **"recommendations"**: Suggestions for reducing bias and improving neutrality.

---

### Task 3: Tone Evaluation
**Instruction:** Evaluate the overall tone of the article. Analyze its sentiment (positive, negative, or neutral) and explain using the following criteria.

#### Criteria:
1. **Emotional Language**  
   - Does the article use emotional or charged language?  
   - **Score Range:** -5 (highly negative) to 5 (highly positive).  
   - **Explanation:** Describe the emotional language and its effect.

2. **Positive or Negative Framing**  
   - Does the article frame individuals or issues positively or negatively?  
   - **Score Range:** -5 (highly negative) to 5 (highly positive).  
   - **Explanation:** Explain the impact of framing.

3. **Use of Humor or Sarcasm**  
   - Is humor or sarcasm used? How does it affect the tone?  
   - **Score Range:** 0 (none) to 5 (frequent use).  
   - **Explanation:** Analyze the influence of humor or sarcasm.

4. **Word Choice and Connotation**  
   - Are specific words or phrases with strong connotations used to influence tone?  
   - **Score Range:** -5 (negative connotation) to 5 (positive connotation).  
   - **Explanation:** Evaluate word choice and its impact.

#### Output:
- **"criteria"**: Dictionary of scores and explanations for each criterion.  
- **"overallToneScore"**: Integer average of the scores, rounded to the nearest whole number. Include reasoning for the overall score.  

---

### Sample JSON Response:

{{
  "politicalLeanEvaluation": {{
    "criteria": {{
      "languageAlignment": {{
        "score": 3,
        "explanation": "The language uses terms like 'social progress' and 'justice,' which are often associated with the Democrat party."
      }},
      "policySupport": {{
        "score": 4,
        "explanation": "The article advocates for policies like universal healthcare, which are typically Democrat-aligned."
      }},
      "politicalFiguresMentioned": {{
        "score": 2,
        "explanation": "The article mentions Democrat figures in a favorable light but includes minimal criticism of Republican figures."
      }},
      "toneAndFraming": {{
        "score": 3,
        "explanation": "The tone is supportive of Democrat-led initiatives, focusing on their benefits."
      }}
    }},
    "overallLeanScore": 3,
    "overallLeanScoreExplanation": "The article leans Democrat based on language, policy emphasis, and tone."
  }},
  "biasEvaluation": {{
    "criteria": {{
      "languageNeutrality": {{
        "score": 1,
        "explanation": "The language is mostly neutral but includes occasional emotional phrases."
      }},
      "balancedRepresentation": {{
        "score": 0,
        "explanation": "The article represents both perspectives fairly evenly."
      }},
      "factVsOpinion": {{
        "score": 2,
        "explanation": "The article relies on verified facts but occasionally includes speculative statements."
      }},
      "sourceAttribution": {{
        "score": 3,
        "explanation": "Most claims are well-sourced, with a few minor exceptions."
      }}
    }},
    "overallBiasScore": 1.5,
    "recommendations": "Ensure neutrality by avoiding speculative statements and focusing on balanced representation."
  }},
  "toneEvaluation": {{
    "criteria": {{
      "emotionalLanguage": {{
        "score": 2,
        "explanation": "The article uses mildly emotional language to emphasize certain points."
      }},
      "positiveOrNegativeFraming": {{
        "score": 3,
        "explanation": "The framing is slightly positive toward Democrat initiatives."
      }},
      "useOfHumorOrSarcasm": {{
        "score": 0,
        "explanation": "The article does not employ humor or sarcasm."
      }},
      "wordChoiceAndConnotation": {{
        "score": 2,
        "explanation": "Word choice conveys optimism toward Democrat-led policies."
      }}
    }},
    "overallToneScore": 2,
    "overallToneScoreExplanation": "The tone is mildly positive, favoring Democrat policies without overt bias."
  }}
}}
""")
            print(response.text)
            try:
                cleaned_response = re.sub(r'^```json|```$', '', response.text, flags=re.MULTILINE).strip()
                lean = float(json.loads(cleaned_response)["politicalLeanEvaluation"]["overallLeanScore"])
                bias = float(json.loads(cleaned_response)["biasEvaluation"]["overallBiasScore"])
                tone = float(json.loads(cleaned_response)["toneEvaluation"]["overallToneScore"])
            except Exception as e:
                print(f"Error occurred: {e}")
                raise e
            print(lean, bias, tone)
            return lean, bias, tone
        except ResourceExhausted:
            print("Quota exhausted. Waiting for 5 seconds before retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"Error occurred: {e}")
            tries += 1
            if tries > 2:
                print("Max retries exceeded. Raising exception...")
                raise e