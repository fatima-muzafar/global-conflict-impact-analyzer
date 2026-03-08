import os
import requests
import pandas as pd

# Ensure data folder exists
if not os.path.exists("../data"):
    os.makedirs("../data")

api_key = "bcadca4cd6584901b2c918ea04261897"

# Simple query to guarantee results
url = f"https://newsapi.org/v2/everything?q=war&language=en&sortBy=publishedAt&apiKey={api_key}"

response = requests.get(url)
data = response.json()

if "articles" in data:
    articles = data['articles'][:20]
    print("Number of articles fetched:", len(articles))
    
    if len(articles) > 0:
        news_df = pd.DataFrame(articles)
        news_df.to_csv("../data/conflict_news.csv", index=False)
        print("✅ Conflict news saved successfully")
    else:
        print("⚠ No articles found for your query. CSV will be empty.")
else:
    print("❌ Error fetching news:", data)