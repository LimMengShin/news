# Unbiased News - A Flask Website with Gemini AI Integration

![demo](https://cloud-jvsjp5lq4-hack-club-bot.vercel.app/0image.png)

---

## Overview

In today's world, many news articles carry some degree of bias—whether intentional or not. This project tackles the challenge of biased reporting by aggregating news articles from diverse publishers and generating an unbiased article. The goal is to create comprehensive articles that fairly represent all viewpoints on a given topic.

## Features

### 1. **Ask Gemini**
Ask Gemini AI to clarify details or gain deeper insights into any part of a news article. This feature helps dispel misconceptions and ensures readers are well-informed.

### 2. **Political Leaning, Bias, and Tone Analysis**
Analyse how an article aligns with political spectrums (e.g., Democrat or Conservative in the US), assess its level of bias, and determine its tone (positive or negative).

### 3. **Convert Your Article**
Input the URL of any news article to transform it into different versions tailored to your preferences:
1. **Unbiased Version:**
A rewritten version that eliminates political bias and presents a balanced perspective, incorporating viewpoints from diverse sources. This version aims to provide a fair and factual representation of the topic.

2. **Opposite Political Leaning:**
An article rewritten such that it reflects the opposing political spectrum (e.g., liberal to conservative or vice versa). This feature is designed to help users identify potential bias by contrasting viewpoints and seeing how facts might be presented differently to align with specific political agendas.

3. **Opposite Tone:**
An article rewritten with the opposite emotional tone (e.g., negative to positive or positive to negative). This allows users to experience news with a different emotional lens, addressing concerns about the predominance of negative reporting in the media.

4. **Simplified Version:**
A concise and easy-to-understand summary of the article, ideal for accessibility or for readers looking for a quick overview without delving into complex details.

### 4. **Search for Articles**

### 5. **Dark Mode**

## Future Improvements

1. Expand the range of news sources to include international publishers.
2. Introduce article categories such as Politics, Business, Technology, etc.
3. ~~Enable users to input a news article link to generate an unbiased version of it.~~ (implemented!)

## Demo

Check out the live demo: [Unbiased News Demo](https://news.mengshin.dev)

## Running the Website

1. Clone this repository and navigate to the project directory.
2. Install the required dependencies:

   ```bash
   pip install Flask google-generativeai python-dotenv newspaper4k lxml-html-clean
   ```

3. Create a `.env` file and add your Gemini API key:

   ```plaintext
   GEMINI_API_KEY="your-key-here"
   ```

4. Start the application:

   ```bash
   flask run
   ```

## Updating the Server

1. Install additional dependencies:

   ```bash
   pip install scikit-learn networkx typing-extensions
   ```

2. Add the [News API key](https://newsapi.org/) to your `.env` file:

   ```plaintext
   NEWS_API_KEY="your-key-here"
   ```

3. Run `update_server.py`, followed by `update_server_2.py`.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python with Flask
- **Database:** SQL

## Credits

1. **Stack Overflow**
2. **ChatGPT**
3. **GitHub Copilot**

(Note: Don't worry, I built most of the project myself! These tools helped primarily with generating prompts for Gemini AI and some support in HTML, CSS, and JavaScript as I'm not too well-versed in those technologies.)

---

### Additional Details for Hack Club

I started this project before discovering Hack Club and had written a bunch of code that was not tracked by Hackatime because I had not installed the extension. However, I accidentally shipped it as a new project without realising there was an option to ship it as an update. Please refer to [this thread](https://hackclub.slack.com/archives/C07PZNMBPBN/p1736486246274139) for more details.
