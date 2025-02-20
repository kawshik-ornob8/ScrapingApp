
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

def scrape_facebook_posts(url, callback, should_stop):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    seen_posts = set()
    try:
        while not should_stop():
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            post_elements = soup.find_all('div', {'data-testid': 'post_message'})
            new_posts = [post.text for post in post_elements if post.text not in seen_posts]
            if new_posts:
                callback(new_posts)
                seen_posts.update(new_posts)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            sleep(2)
    finally:
        driver.quit()