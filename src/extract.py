from groq import Groq
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_insights(article: dict) -> dict:
    # Use full_text if available, fall back to description
    content = article.get("full_text") or article.get("description") or ""

    prompt = f"""
You are a news analyst. Given this article, return ONLY a JSON object with:
- "summary": one sentence summary (max 30 words)
- "topics": list of 3 topic tags (e.g. ["AI", "regulation", "Google"])
- "sentiment": one of "positive", "negative", "neutral"
- "key_entities": list of up to 3 important people or companies mentioned

Article title: {article['title']}
Article content: {content[:2000]}

Return only the JSON, no extra text, no markdown backticks.
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    insights = json.loads(raw)
    return {**article, **insights}

def process_articles(articles: list) -> list:
    results = []
    for i, article in enumerate(articles):
        try:
            result = extract_insights(article)
            results.append(result)
            print(f"Extracted insights {i+1}/{len(articles)}: {article['title'][:50]}")
            time.sleep(3)
        except Exception as e:
            print(f"Skipping article due to error: {e}")
    return results