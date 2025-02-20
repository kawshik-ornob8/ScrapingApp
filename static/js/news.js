let newsScraping = false;
let pollingInterval;

function startNewsScraping() {
    const url = document.getElementById('news-url').value;
    if (!isValidSitemapUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid news sitemap URL (e.g., ending with sitemap.xml)', 'error');
        return;
    }
    newsScraping = true;
    toggleScrapingControls(true);
    fetch('/scrape/news', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to start scraping');
            return response.json();
        })
        .then(data => {
            if (data.status === 'Scraping started') {
                pollingInterval = setInterval(updateProgress, 500);
            }
        })
        .catch(handleError);
}

function stopScraping() {
    fetch('/stop-scraping', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Scraping stopped') {
                clearInterval(pollingInterval);
                toggleScrapingControls(false);
            }
        });
}

function updateProgress() {
    fetch('/get_progress')
        .then(response => response.json())
        .then(data => {
            const progressBar = document.getElementById('progress-bar');
            progressBar.style.width = `${data.progress}%`;
            document.getElementById('results').innerHTML = data.comments.map(item => `
                <div class="col-12">
                    <div class="card mb-2 animate__animated animate__fadeIn">
                        <div class="card-body">
                            <strong>${item.title}</strong><br>${item.content}
                        </div>
                    </div>
                </div>
            `).join('');
            if (!data.scraping) {
                clearInterval(pollingInterval);
                toggleScrapingControls(false);
            }
        });
}

function isValidSitemapUrl(url) {
    return /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\/.*sitemap.*\.xml$/.test(url);
}

function exportData(format) {
    window.location.href = `/export/${format}`;
}

function toggleScrapingControls(scraping) {
    document.getElementById('start-btn').disabled = scraping;
    document.getElementById('stop-btn').disabled = !scraping;
}

function handleError(error) {
    Swal.fire('Error', error.message, 'error');
    newsScraping = false;
    toggleScrapingControls(false);
}