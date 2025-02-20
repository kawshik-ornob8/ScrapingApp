from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from scraping.youtube_scraper import YouTubeScraper
from scraping.facebook_scraper import scrape_facebook_posts
from scraping.twitter_scraper import scrape_twitter_posts
from scraping.website_scraper import scrape_website_content
from scraping.news_scraper import scrape_news_articles
from utils import save_as_excel, save_as_word
from config import Config
import threading
import re
import time
import logging

logger = logging.getLogger(__name__)

class ScrapingManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = []
        self.scraping = False
        self.platform = None
        self.start_time = None
        self.limit = None
        self.element_type = None
        
    def start_scraping(self, platform, limit=None, element_type='text'):
        with self.lock:
            self.scraping = True
            self.platform = platform
            self.start_time = time.time()
            self.data.clear()
            self.limit = limit
            self.element_type = element_type
            
    def stop_scraping(self):
        with self.lock:
            self.scraping = False
            
    def add_data(self, items):
        with self.lock:
            self.data.extend(items)
            logger.info(f"Added {len(items)} items, total now: {len(self.data)}")
            
    def get_progress(self):
        with self.lock:
            return {
                'count': len(self.data),
                'comments': self.data[-10:] if len(self.data) >= 10 else self.data,
                'scraping': self.scraping,
                'platform': self.platform,
                'elapsed': time.time() - self.start_time if self.start_time else 0,
                'limit': self.limit,
                'element_type': self.element_type
            }
    
    def get_all_data(self):
        with self.lock:
            return self.data

manager = ScrapingManager()

def validate_url(url, platform):
    domain_patterns = {
        'youtube': r'(youtube\.com|youtu\.be)',
        'facebook': r'(facebook\.com|fb\.me)',
        'twitter': r'(twitter\.com|x\.com)',
        'news': r'(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\/.*sitemap.*\.xml$',  # For sitemap URLs
        'website': r'(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    }
    pattern = domain_patterns.get(platform)
    return bool(pattern and re.search(pattern, url, re.IGNORECASE))

def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        return render_template('index.html')

    @app.route('/youtube')
    def youtube():
        return render_template('youtube.html')

    @app.route('/facebook')
    def facebook():
        return render_template('facebook.html')

    @app.route('/twitter')
    def twitter():
        return render_template('twitter.html')

    @app.route('/website')
    def website():
        return render_template('website.html')

    @app.route('/news')
    def news():
        return render_template('news.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/scrape/youtube', methods=['POST'])
    def scrape_youtube():
        data = request.json
        url = data.get('url')
        api_key = data.get('api_key', None)
        limit = data.get('limit', None)
        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0:
                    return jsonify({'error': 'Limit must be positive'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid limit value'}), 400
        if not validate_url(url, 'youtube'):
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        if manager.scraping:
            return jsonify({'error': 'Scraping already in progress'}), 400
        manager.start_scraping('youtube', limit)
        scraper = YouTubeScraper(api_key if api_key is not None else Config.YOUTUBE_API_KEY)
        thread = threading.Thread(target=scraper.scrape_comments, args=(url, manager.add_data, limit))
        thread.start()
        return jsonify({'status': 'Scraping started'}), 202

    @app.route('/scrape/facebook', methods=['POST'])
    def scrape_facebook():
        data = request.json
        url = data.get('url')
        if not validate_url(url, 'facebook'):
            return jsonify({'error': 'Invalid Facebook URL'}), 400
        if manager.scraping:
            return jsonify({'error': 'Scraping already in progress'}), 400
        manager.start_scraping('facebook')
        thread = threading.Thread(target=scrape_facebook_posts, args=(url, manager.add_data, lambda: not manager.scraping))
        thread.start()
        return jsonify({'status': 'Scraping started'}), 202

    @app.route('/scrape/twitter', methods=['POST'])
    def scrape_twitter():
        data = request.json
        url = data.get('url')
        if not validate_url(url, 'twitter'):
            return jsonify({'error': 'Invalid Twitter URL'}), 400
        if manager.scraping:
            return jsonify({'error': 'Scraping already in progress'}), 400
        manager.start_scraping('twitter')
        thread = threading.Thread(target=scrape_twitter_posts, args=(url, manager.add_data, lambda: not manager.scraping))
        thread.start()
        return jsonify({'status': 'Scraping started'}), 202

    @app.route('/scrape/website', methods=['POST'])
    def scrape_website():
        data = request.json
        url = data.get('url')
        element_type = data.get('element_type', 'text')
        if not validate_url(url, 'website'):
            return jsonify({'error': 'Invalid Website URL'}), 400
        if manager.scraping:
            return jsonify({'error': 'Scraping already in progress'}), 400
        manager.start_scraping('website', element_type=element_type)
        thread = threading.Thread(target=lambda: manager.add_data(scrape_website_content(url, element_type)))
        thread.start()
        return jsonify({'status': 'Scraping started'}), 202

    @app.route('/download/<filename>')
    def download_file(filename):
        return send_file(filename, as_attachment=True)

    @app.route('/scrape/news', methods=['POST'])
    def scrape_news():
        data = request.json
        url = data.get('url')
        if not validate_url(url, 'news'):
            return jsonify({'error': 'Invalid News Sitemap URL'}), 400
        if manager.scraping:
            return jsonify({'error': 'Scraping already in progress'}), 400
        manager.start_scraping('news')
        thread = threading.Thread(target=scrape_news_articles, args=(url, manager.add_data))
        thread.start()
        return jsonify({'status': 'Scraping started'}), 202

    @app.route('/stop-scraping', methods=['POST'])
    def stop_scraping():
        if manager.scraping:
            manager.stop_scraping()
        return jsonify({'status': 'Scraping stopped'}), 200

    @app.route('/get_progress')
    def get_progress():
        progress = manager.get_progress()
        return jsonify({
            'count': progress['count'],
            'comments': progress['comments'],
            'progress': min(progress['count'] / (progress['limit'] or 100) * 100, 100) if progress['count'] else 0,
            'scraping': progress['scraping'],
            'platform': progress['platform'],
            'limit': progress['limit'],
            'element_type': progress['element_type']
        })

    @app.route('/export/<format>')
    def export_data(format):
        data = manager.get_all_data()
        if not data:
            return jsonify({'error': 'No data to export'}), 400
        if format == 'excel':
            filename = save_as_excel(data)
        elif format == 'word':
            filename = save_as_word(data)
        elif format == 'zip' and manager.element_type == 'images':
            filename = data[0]
        else:
            return jsonify({'error': 'Invalid format'}), 400
        return send_file(filename, as_attachment=True)