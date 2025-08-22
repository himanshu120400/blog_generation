from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def fetch_website_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        print("Initializing browser for scraping")
        driver = webdriver.Chrome(options=chrome_options)
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        driver.get(url)
        time.sleep(5) 
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
            
        content = ' '.join(soup.stripped_strings)

        if content:
            print("Successfully fetched and parsed website content.")
            return content
        else:
            print(f"Could not extract meaningful content from {url}, even after rendering.")
            return None

    except Exception as e:
        print(f"An error occurred during web scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()