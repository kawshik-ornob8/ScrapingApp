
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

def scrape_twitter_posts(url, callback, should_stop):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    seen_tweets = set()
    try:
        while not should_stop():
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tweet_elements = soup.find_all('div', {'data-testid': 'tweetText'})
            new_tweets = [tweet.text for tweet in tweet_elements if tweet.text not in seen_tweets]
            if new_tweets:
                callback(new_tweets)
                seen_tweets.update(new_tweets)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            sleep(2)
    finally:
        driver.quit()