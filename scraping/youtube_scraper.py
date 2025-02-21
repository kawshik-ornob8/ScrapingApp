import re
import requests
import time
import logging
from config import Config  # Import Config to use the API key from .env

logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self, user_api_key=None):
        self.default_api_key = Config.YOUTUBE_API_KEY  # Use the key from config/.env
        self.api_key = user_api_key if user_api_key else self.default_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        self.comments_url = "https://www.googleapis.com/youtube/v3/comments"
        self.running = False

    def extract_video_id(self, url):
        patterns = [r"(?:v=|\/)([0-9A-Za-z_-]{11})", r"youtu\.be\/([0-9A-Za-z_-]{11})"]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def fetch_all_replies(self, parent_id, total_reply_count, callback):
        reply_params = {
            'part': 'snippet',
            'parentId': parent_id,
            'key': self.api_key,
            'maxResults': 100
        }
        all_replies_count = 0
        while self.running and all_replies_count < total_reply_count:
            try:
                response = requests.get(self.comments_url, params=reply_params)
                response.raise_for_status()
                data = response.json()
                for reply in data.get('items', []):
                    reply_text = reply['snippet']['textDisplay']
                    callback([reply_text])
                    all_replies_count += 1
                    logger.debug(f"Sent reply for parent {parent_id}, total: {all_replies_count}/{total_reply_count}")
                    if all_replies_count >= total_reply_count:
                        break
                if 'nextPageToken' in data and all_replies_count < total_reply_count:
                    reply_params['pageToken'] = data['nextPageToken']
                    time.sleep(1)
                else:
                    break
            except requests.exceptions.RequestException as e:
                logger.error(f"Reply fetch failed: {str(e)}")
                break

    def scrape_comments(self, url, callback, limit=10000):
        self.running = True
        video_id = self.extract_video_id(url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {url}")
            return
        params = {
            'part': 'snippet,replies',
            'videoId': video_id,
            'key': self.api_key,
            'maxResults': 100,
            'order': 'relevance'
        }
        total_comments = 0
        page_count = 0
        try:
            while self.running:
                page_count += 1
                logger.info(f"Fetching commentThreads page {page_count} with params: {params}")
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                logger.debug(f"API Response Keys: {data.keys()}")

                if "error" in data:
                    logger.error(f"API Error: {data['error']['message']}")
                    break

                items = data.get('items', [])
                if not items:
                    logger.info("No more commentThreads returned by API")
                    break

                for item in items:
                    top_comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    callback([top_comment])
                    total_comments += 1
                    logger.info(f"Sent top-level comment, total: {total_comments}")

                    if limit and total_comments >= limit:
                        logger.info(f"Reached user-defined limit: {limit} comments")
                        break

                    total_reply_count = item['snippet']['totalReplyCount']
                    if total_reply_count > 0:
                        parent_id = item['snippet']['topLevelComment']['id']
                        self.fetch_all_replies(parent_id, total_reply_count, callback)
                        total_comments += total_reply_count
                        logger.info(f"Total comments after replies: {total_comments}")

                    if limit and total_comments >= limit:
                        logger.info(f"Reached user-defined limit: {limit} comments")
                        break

                if limit and total_comments >= limit:
                    break

                if 'nextPageToken' in data:
                    params['pageToken'] = data['nextPageToken']
                    logger.info(f"Next page token found: {params['pageToken']}")
                    time.sleep(1)
                else:
                    logger.info("No nextPageToken in response, stopping")
                    break
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
        finally:
            self.running = False
            logger.info(f"Scraping completed. Total comments collected: {total_comments}")

    def stop_scraping(self):
        self.running = False
