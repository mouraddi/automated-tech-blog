import os
import datetime
import feedparser
from slugify import slugify
from google import genai

# 1. Initialize Gemini Client using the API key stored in Windows environment variables
client = genai.Client()

# 2. List of tech RSS feeds
RSS_FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/"
]

def fetch_latest_news():
    """Fetch the latest news title, link, and summary from RSS feeds"""
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            first_entry = feed.entries[0]
            return first_entry.title, first_entry.link, first_entry.get('summary', '')
    return None, None, None

def generate_hugo_post(title, link, summary):
    prompt = f"""
    You are an expert technical editor writing for an open-source tools and AI news directory.
    Write a high-quality blog post in English based on this technical news item.

    Title: {title}
    Source URL: {link}
    Summary Context: {summary}

    OUTPUT FORMAT MUST BE VALID HUGO FRONT MATTER FOLLOWED BY MARKDOWN:

    ---
    title: "{title}"
    date: {datetime.date.today().isoformat()}
    draft: false
    tags: ["Open Source", "AI", "Tech News"]
    summary: "Brief 2-sentence summary of {title}"
    ---

    ## Overview
    (Write a concise overview in English)

    ## Key Highlights
    - (Feature/Highlight 1)
    - (Feature/Highlight 2)
    - (Feature/Highlight 3)

    ## Source Link
    Read the full story on [Original Source]({link}).
    """

    print(f"Generating article in English for: {title}...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    news_title, news_link, news_summary = fetch_latest_news()
    
    if news_title:
        post_md = generate_hugo_post(news_title, news_link, news_summary)
        
        # Save the post as a Markdown file inside the Hugo posts directory
        filename = f"{slugify(news_title[:50])}.md"
        output_path = os.path.join("content", "posts", filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(post_md)
            
        print(f"✅ Success! Post saved to: {output_path}")
    else:
        print("No new content found.")