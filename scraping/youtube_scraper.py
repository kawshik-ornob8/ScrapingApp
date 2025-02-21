import re
import requests
import time
import logging
from config import Config

logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self, user_api_key=None):
        self.default_api_key = Config.YOUTUBE_API_KEY
        self.api_key = user_api_key if user_api_key else self.default_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        self.comments_url = "https://www.googleapis.com/youtube/v3/comments"

    @staticmethod
    def extract_video_id(url):
        patterns = [r"(?:v=|\/)([0-9A-Za-z_-]{11})", r"youtu\.be\/([0-9A-Za-z_-]{11})"]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def fetch_comment_page(self, video_id, page_token=None, limit=100):
        params = {
            'part': 'snippet,replies',
            'videoId': video_id,
            'key': self.api_key,
            'maxResults': min(limit, 100),
            'order': 'relevance'
        }
        if page_token:
            params['pageToken'] = page_token
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                logger.error(f"API Error: {data['error']['message']}")
                return [], None
            comments = []
            for item in data.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(top_comment)
                # Optionally handle replies if needed
            next_page_token = data.get('nextPageToken', None)
            return comments, next_page_token
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return [], None