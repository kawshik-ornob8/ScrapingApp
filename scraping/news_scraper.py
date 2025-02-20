import requests
import time
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def fetch_news_urls(sitemap_url):
    """Fetch all article URLs from a sitemap XML."""
    try:
        response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "xml")
        urls = [loc.text for loc in soup.find_all("loc") if loc.text and not loc.text.endswith(('.jpg', '.png', '.gif'))]
        logger.info(f"Fetched {len(urls)} URLs from sitemap: {sitemap_url}")
        return urls
    except Exception as e:
        logger.error(f"Error fetching sitemap {sitemap_url}: {str(e)}")
        return []

def scrape_article(url):
    """Scrape the title and content of a news article."""
    try:
        # Skip if URL is an image
        if url.endswith(('.jpg', '.png', '.gif')):
            logger.debug(f"Skipping image URL: {url}")
            return None
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title").text.strip() if soup.find("title") else "No Title"
        body = soup.find("article") or soup.find("div", class_=re.compile("content|article|story|post"))
        text = ' '.join([p.get_text(strip=True) for p in body.find_all("p")]) if body else "No Content"
        return {'title': title, 'content': text}
    except Exception as e:
        logger.error(f"Error scraping article {url}: {str(e)}")
        return None

def scrape_news_articles(sitemap_url, callback=None):
    """Scrape news articles from a sitemap URL."""
    news_urls = fetch_news_urls(sitemap_url)
    if not news_urls:
        logger.warning(f"No URLs found in sitemap: {sitemap_url}")
        return
    
    for news_url in news_urls:
        article = scrape_article(news_url)
        if article and callback:
            callback([article])
            logger.info(f"Scraped article: {news_url}")
        time.sleep(1)  # Rate limiting