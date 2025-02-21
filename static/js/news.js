let collectedArticles = [];
let isScraping = false;

async function startNewsScraping() {
    const sitemapUrl = document.getElementById('news-url').value;
    if (!isValidSitemapUrl(sitemapUrl)) {
        Swal.fire('Invalid URL', 'Please enter a valid news sitemap URL', 'error');
        return;
    }
    isScraping = true;
    toggleScrapingControls(true);
    collectedArticles = [];
    const urlsResponse = await fetch('/scrape/news/urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sitemap_url: sitemapUrl })
    });
    const urlsData = await urlsResponse.json();
    if (urlsData.error) {
        Swal.fire('Error', urlsData.error, 'error');
        isScraping = false;
        toggleScrapingControls(false);
        return;
    }
    const articleUrls = urlsData.urls;
    const batchSize = 10;
    for (let i = 0; i < articleUrls.length && isScraping; i += batchSize) {
        const batchUrls = articleUrls.slice(i, i + batchSize);
        const batchResponse = await fetch('/scrape/news/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ article_urls: batchUrls })
        });
        const batchData = await batchResponse.json();
        if (batchData.error) {
            Swal.fire('Error', batchData.error, 'error');
            break;
        }
        collectedArticles = collectedArticles.concat(batchData.articles);
        updateProgress(collectedArticles.length, articleUrls.length);
    }
    isScraping = false;
    toggleScrapingControls(false);
}

function updateProgress(count, total) {
    const progress = (count / total) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('results').innerHTML = collectedArticles.slice(-10).map(article => `
        <div class="col-12"><div class="card mb-2"><div class="card-body"><strong>${article.title}</strong><br>${article.content}</div></div></div>
    `).join('');
}

function stopScraping() {
    isScraping = false;
    toggleScrapingControls(false);
}

function isValidSitemapUrl(url) {
    return /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\/.*sitemap.*\.xml$/.test(url);
}

function exportData(format) {
    fetch(`/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: collectedArticles })
    }).then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Export failed');
    }).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scraped_data.${format}`;
        a.click();
    }).catch(error => {
        Swal.fire('Error', error.message, 'error');
    });
}

function toggleScrapingControls(scraping) {
    document.getElementById('start-btn').disabled = scraping;
    document.getElementById('stop-btn').disabled = !scraping;
}