import yaml
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import json
import feedparser
from datetime import datetime

LOG_FILE = "fetch_log.json"

def load_sources():
    with open("crewai_config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config["sources"]

def is_recent(pubdate, days=7):
    try:
        for fmt in ("%Y-%m-%d", "%d %b %Y", "%b %d, %Y"):
            try:
                dt = datetime.strptime(pubdate.strip(), fmt)
                break
            except ValueError:
                continue
        else:
            return False
        return (datetime.now() - dt).days <= days
    except Exception:
        return False

def load_fetch_log():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_fetch_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def should_include_article(company, article_id, fetch_log):
    fetched = fetch_log.get(company, [])
    if article_id in fetched:
        return False
    fetched.append(article_id)
    fetch_log[company] = fetched
    save_fetch_log(fetch_log)
    return True

def fetch_arxiv_api(keywords, days=7, max_results=5):
    query = "+AND+".join([f"all:{kw}" for kw in keywords])
    query_encoded = quote_plus(query)
    url = f"http://export.arxiv.org/api/query?search_query={query_encoded}&sortBy=submittedDate&sortOrder=descending&max_results=25"

    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        published = entry.published
        entry_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.now() - entry_date).days > days:
            continue
        results.append({
            "title": entry.title,
            "publication_date": published[:10],
            "link": entry.link,
            "source": "arXiv",
            "content": entry.summary
        })
        if len(results) >= max_results:
            break
    return results

def scrape_semantic_scholar(query, company, fetch_log, max_results=5):
    url = f"https://www.semanticscholar.org/search?q={query}&sort=recency"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    articles = soup.select('div.cl-paper-row') or soup.select('div.search-result')
    for entry in articles[:max_results * 2]:
        title_elem = entry.find('a', class_='cl-paper-title') or entry.find('a', class_='search-result-title')
        title = title_elem.get_text(strip=True) if title_elem else "No title"
        link = "https://www.semanticscholar.org" + title_elem.get("href") if title_elem else ""
        summary_elem = entry.find('div', class_='cl-paper-abstract') or entry.find('div', class_='search-result-abstract')
        summary = summary_elem.get_text(strip=True) if summary_elem else ""
        year_elem = entry.find('span', class_='cl-paper-pubyear') or entry.find('span', class_='search-result-year')
        pubdate_str = year_elem.get_text(strip=True) if year_elem else ""
        if pubdate_str and not is_recent(pubdate_str, 7):
            continue
        if not should_include_article(company, link, fetch_log):
            continue
        results.append({
            "title": title,
            "publication_date": pubdate_str,
            "link": link,
            "source": "SemanticScholar",
            "content": summary
        })
        if len(results) >= max_results:
            break
    return results

def scrape_acm(query, company, fetch_log, max_results=5):
    url = f"https://dl.acm.org/action/doSearch?AllField={query}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select('.search__item')[:max_results*2]:
        title_elem = item.find('h5')
        title = title_elem.get_text(strip=True) if title_elem else ""
        link = "https://dl.acm.org" + item.find('a').get('href') if item.find('a') else ""
        summary_elem = item.find('div', class_='issue-item__abstract')
        summary = summary_elem.get_text(strip=True) if summary_elem else ""
        pubdate_elem = item.find('span', class_='bookPubDate') or item.find('span', class_='epub-section__date')
        pubdate_str = pubdate_elem.get_text(strip=True) if pubdate_elem else ""
        if pubdate_str and not is_recent(pubdate_str, 7):
            continue
        if not should_include_article(company, link, fetch_log):
            continue
        results.append({
            "title": title,
            "publication_date": pubdate_str,
            "link": link,
            "source": "ACM",
            "content": summary
        })
        if len(results) >= max_results:
            break
    return results

def scrape_google_scholar(query, company, fetch_log, max_results=5):
    url = f"https://scholar.google.com/scholar?q={query}&as_ylo={datetime.now().year}"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select('.gs_ri')[:max_results*2]:
        title_elem = item.find('h3', class_='gs_rt')
        title = title_elem.get_text(strip=True) if title_elem else ""
        link = title_elem.find('a')['href'] if title_elem and title_elem.find('a') else ""
        summary = item.find('div', class_='gs_rs').get_text(strip=True) if item.find('div', class_='gs_rs') else ""
        pubdate_elem = item.find('div', class_='gs_a')
        pubdate_str = ""
        if pubdate_elem:
            import re
            match = re.search(r"\b(20\d{2}|19\d{2})\b", pubdate_elem.get_text())
            pubdate_str = match.group(1) if match else ""
        if pubdate_str and not is_recent(pubdate_str, 7):
            continue
        if not should_include_article(company, link, fetch_log):
            continue
        results.append({
            "title": title,
            "publication_date": pubdate_str,
            "link": link,
            "source": "Google Scholar",
            "content": summary
        })
        if len(results) >= max_results:
            break
    return results

def fetch_articles_and_info(keywords_and_industry, company_name="company"):
    import re
    match = re.search(r"Keywords:\s*(.*)", keywords_and_industry, re.I)
    keywords = [k.strip() for k in match.group(1).split(",") if k.strip()] if match else []
    query = "+".join(keywords)
    sources = load_sources()
    fetch_log = load_fetch_log()
    all_results = []
    for source in sources:
        print(f"[INFO] Scraping {source['name']}...")
        if source['name'] == "arxiv":
            results = fetch_arxiv_api(keywords, days=7, max_results=5)
        elif source['name'] == "semantic_scholar":
            results = scrape_semantic_scholar(query, company_name, fetch_log)
        elif source['name'] == "acm":
            results = scrape_acm(query, company_name, fetch_log)
        elif source['name'] == "google_scholar":
            results = scrape_google_scholar(query, company_name, fetch_log)
        else:
            results = []
        all_results.extend(results)
    if not all_results:
        print("No articles found in last 7 days from major sources.")
    return all_results