// O:\Flask\scrape\static\js\twitter.js
let twitterScraping = false;
let pollingInterval;

function startTwitterScraping() {
    const url = document.getElementById('twitter-url').value;
    if (!isValidTwitterUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid Twitter URL', 'error');
        return;
    }
    twitterScraping = true;
    toggleScrapingControls(true);
    fetch('/scrape/twitter', {
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
                pollingInterval = setInterval(updateProgress, 1000);
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
            document.getElementById('results').innerHTML = data.comments.map(comment => `
                <div class="col-12"><div class="card mb-2 animate__animated animate__fadeIn"><div class="card-body">${comment}</div></div></div>
            `).join('');
            if (!data.scraping) {
                clearInterval(pollingInterval);
                toggleScrapingControls(false);
            }
        });
}

function isValidTwitterUrl(url) {
    return /^(https?:\/\/)?(www\.)?(twitter\.com|x\.com)\/.+/.test(url);
}