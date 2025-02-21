let collectedComments = [];
let isScraping = false;

function startScraping() {
    const url = document.getElementById('youtube-url').value;
    const apiKey = document.getElementById('api-key').value;
    let limit = document.getElementById('limit').value || 10000;
    limit = Math.min(parseInt(limit), 10000);
    if (!isValidYouTubeUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid YouTube URL', 'error');
        return;
    }
    isScraping = true;
    toggleScrapingControls(true);
    collectedComments = [];
    let pageToken = null;
    async function fetchPage() {
        if (!isScraping) return;
        const response = await fetch('/scrape/youtube/page', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, page_token: pageToken, limit: limit - collectedComments.length, api_key: apiKey })
        });
        const data = await response.json();
        if (data.error) {
            Swal.fire('Error', data.error, 'error');
            isScraping = false;
            toggleScrapingControls(false);
            return;
        }
        collectedComments = collectedComments.concat(data.comments);
        updateProgress(collectedComments.length, limit);
        pageToken = data.next_page_token;
        if (pageToken && collectedComments.length < limit) {
            setTimeout(fetchPage, 500);
        } else {
            isScraping = false;
            toggleScrapingControls(false);
        }
    }
    fetchPage();
}

function updateProgress(count, limit) {
    const progress = (count / limit) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('user-limit').innerText = limit;
    document.getElementById('comments-collected').innerText = count;
    document.getElementById('results').innerHTML = collectedComments.slice(-10).map(comment => `
        <div class="col-12"><div class="card mb-2"><div class="card-body">${comment}</div></div></div>
    `).join('');
}

function stopScraping() {
    isScraping = false;
    toggleScrapingControls(false);
}

function isValidYouTubeUrl(url) {
    return /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/.test(url);
}

function exportData(format) {
    fetch(`/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: collectedComments })
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