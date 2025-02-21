from flask import Flask, render_template, request, jsonify, send_file
from scraping.youtube_scraper import YouTubeScraper
from scraping.news_scraper import fetch_news_urls, scrape_article
from scraping.website_scraper import scrape_website_content
from utils import save_as_excel, save_as_word
from config import Config
import re
import logging

logger = logging.getLogger(__name__)

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

    @app.route('/scrape/youtube/page', methods=['POST'])
    def scrape_youtube_page():
        data = request.json
        url = data.get('url')
        page_token = data.get('page_token', None)
        limit = data.get('limit', 100)
        api_key = data.get('api_key', Config.YOUTUBE_API_KEY)
        if not url:
            return jsonify({'error': 'Missing URL'}), 400
        video_id = YouTubeScraper.extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        scraper = YouTubeScraper(api_key)
        comments, next_page_token = scraper.fetch_comment_page(video_id, page_token, limit)
        return jsonify({'comments': comments, 'next_page_token': next_page_token})

    @app.route('/scrape/news/urls', methods=['POST'])
    def get_news_urls():
        data = request.json
        sitemap_url = data.get('sitemap_url')
        if not sitemap_url:
            return jsonify({'error': 'Missing sitemap_url'}), 400
        if not validate_url(sitemap_url, 'news'):
            return jsonify({'error': 'Invalid News Sitemap URL'}), 400
        urls = fetch_news_urls(sitemap_url)
        return jsonify({'urls': urls})

    @app.route('/scrape/news/batch', methods=['POST'])
    def scrape_news_batch():
        data = request.json
        article_urls = data.get('article_urls', [])
        if not article_urls:
            return jsonify({'error': 'Missing article_urls'}), 400
        articles = []
        for url in article_urls:
            article = scrape_article(url)
            if article:
                articles.append(article)
        return jsonify({'articles': articles})

    @app.route('/scrape/website', methods=['POST'])
    def scrape_website():
        data = request.json
        url = data.get('url')
        element_type = data.get('element_type', 'text')
        if not validate_url(url, 'website'):
            return jsonify({'error': 'Invalid Website URL'}), 400
        data = scrape_website_content(url, element_type)
        return jsonify({'data': data})

    @app.route('/export/<format>', methods=['POST'])
    def export_data(format):
        data = request.json.get('data', [])
        if not data:
            return jsonify({'error': 'No data to export'}), 400
        if format == 'excel':
            filename = save_as_excel(data)
        elif format == 'word':
            filename = save_as_word(data)
        elif format == 'zip' and isinstance(data[0], str) and data[0].endswith('.zip'):
            filename = data[0]
        else:
            return jsonify({'error': 'Invalid format'}), 400
        return send_file(filename, as_attachment=True)

    # Disabled unsupported routes (Facebook, Twitter)
    @app.route('/scrape/facebook', methods=['POST'])
    def scrape_facebook():
        return jsonify({'error': 'Facebook scraping is not supported on Vercel due to Selenium limitations'}), 400

    @app.route('/scrape/twitter', methods=['POST'])
    def scrape_twitter():
        return jsonify({'error': 'Twitter scraping is not supported on Vercel due to Selenium limitations'}), 400