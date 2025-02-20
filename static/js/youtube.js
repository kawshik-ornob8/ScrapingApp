let youtubeScraping = false;
let pollingInterval;

function startScraping() {
    const url = document.getElementById('youtube-url').value;
    const apiKey = document.getElementById('api-key').value;
    let limit = document.getElementById('limit').value || 10000; // Default to 10,000
    if (!isValidYouTubeUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid YouTube URL', 'error');
        return;
    }
    if (limit && (isNaN(limit) || limit <= 0)) {
        Swal.fire('Invalid Limit', 'Please enter a positive number', 'error');
        return;
    }
    limit = Math.min(parseInt(limit), 10000); // Cap at 10,000
    youtubeScraping = true;
    toggleScrapingControls(true);
    fetch('/scrape/youtube', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, api_key: apiKey, limit: limit })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to start scraping');
            return response.json();
        })
        .then(data => {
            if (data.status === 'Scraping started') {
                pollingInterval = setInterval(updateProgress, 500); // Reduced to 500ms for real-time feel
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
            progressBar.textContent = `${Math.round(data.progress)}%`;
            document.getElementById('user-limit').innerText = data.limit || '10000';
            document.getElementById('comments-collected').innerText = data.count;
            document.getElementById('results').innerHTML = data.comments.map(comment => `
                <div class="col-12"><div class="card mb-2 animate__animated animate__fadeIn"><div class="card-body">${comment}</div></div></div>
            `).join('');
            if (!data.scraping) {
                clearInterval(pollingInterval);
                toggleScrapingControls(false);
                if (data.limit !== null && data.count == data.limit) {
                    exportData('excel');
                }
            }
        });
}

function isValidYouTubeUrl(url) {
    return /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/.test(url);
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
    youtubeScraping = false;
    toggleScrapingControls(false);
}