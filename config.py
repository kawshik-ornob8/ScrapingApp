import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY') 
    MAX_COMMENTS = 500
    REQUEST_TIMEOUT = 10
    RATE_LIMIT_DELAY = 0.5
    ALLOWED_DOMAINS = {
        'youtube': ['youtube.com', 'youtu.be'],
        'facebook': ['facebook.com', 'fb.me'],
        'twitter': ['twitter.com', 'x.com'],
        'news': ['bbc.com', 'nytimes.com', 'reuters.com'],
        'website': []
    }