import requests
import os
import time
from newspaper import Article
from dotenv import load_dotenv

load_dotenv()

def get_full_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        return text[:3000] if text else ""
    except Exception as e:
        print(f"Could not scrape {url}: {e}")
        return ""

def fetch_articles(topic: str = "artificial intelligence", page_size: int = 20) -> list:
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "pageSize": page_size,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": os.getenv("NEWS_API_KEY")
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    articles = response.json().get("articles", [])

    cleaned = []
    for i, a in enumerate(articles):
        print(f"Scraping article {i+1}/{len(articles)}: {a.get('title', '')[:50]}")
        full_text = get_full_text(a.get("url", ""))
        time.sleep(1)
        cleaned.append({
            "title":        a.get("title", ""),
            "description":  a.get("description", ""),
            "full_text":    full_text,
            "url":          a.get("url", ""),
            "published_at": a.get("publishedAt", ""),
            "source":       a.get("source", {}).get("name", "")
        })

    return cleaned

if __name__ == "__main__":
    articles = fetch_articles(page_size=3)
    for a in articles:
        print("---")
        print("Title:", a["title"])
        print("Full text length:", len(a["full_text"]), "chars")
        print("Preview:", a["full_text"][:200])