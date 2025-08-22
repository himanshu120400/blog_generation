import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def fetch_recent_news(keywords_and_industry, days=7, company=None):
    import re
    kw_match = re.search(r"Keywords:\s*(.*)", keywords_and_industry, re.I)
    keywords = [k.strip() for k in kw_match.group(1).split(",") if k.strip()] if kw_match else []
    if not keywords:
        keywords = []
    if company:
        keywords.append(company)

    news_results = []
    search_url = "https://news.google.com/search?q={kw}%20when:{days}d&hl=en-US&gl=US&ceid=US:en"
    for kw in keywords:
        url = search_url.format(kw=kw.replace(" ", "%20"), days=days)
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            for article in soup.select("article"):
                title = article.text[:100]
                link = ""
                for a in article.find_all("a"):
                    if a.get("href", "").startswith("./articles"):
                        link = "https://news.google.com" + a.get("href", "")[1:]
                        break
                news_results.append({
                    "title": title,
                    "link": link,
                    "source": "Google News",
                    "content": title
                })
        except Exception as e:
            print(f"[News Fetch ERROR] {e}")
            continue
        
    return news_results[:8]