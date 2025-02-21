import requests
from bs4 import BeautifulSoup
import os
import shutil
import zipfile

def scrape_website_content(url, element_type='text'):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if element_type == 'text':
            paragraphs = soup.find_all('p')
            return [p.text.strip() for p in paragraphs if p.text.strip()]
        elif element_type == 'headlines':
            headlines = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            return [h.text.strip() for h in headlines if h.text.strip()]
        elif element_type == 'images':
            images = soup.find_all('img')
            img_urls = []
            for img in images:
                if 'src' in img.attrs:
                    img_url = img['src']
                    if not img_url.startswith(('http://', 'https://')):
                        base_url = url if url.endswith('/') else url + '/'
                        img_url = base_url + img_url if img_url.startswith('/') else base_url + '/' + img_url
                    img_urls.append(img_url)
            
            img_dir = 'temp_images'
            os.makedirs(img_dir, exist_ok=True)
            for i, img_url in enumerate(img_urls):
                try:
                    img_response = requests.get(img_url, timeout=10)
                    img_response.raise_for_status()
                    with open(os.path.join(img_dir, f'image_{i}.jpg'), 'wb') as f:
                        f.write(img_response.content)
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")
            
            zip_filename = 'images.zip'
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(img_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            shutil.rmtree(img_dir)
            return [zip_filename]
        else:
            return []
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []