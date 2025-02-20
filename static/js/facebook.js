let facebookScraping = false;
let pollingInterval;

function startFacebookScraping() {
    const url = document.getElementById('facebook-url').value;
    if (!isValidFacebookUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid Facebook URL', 'error');
        return;
    }
    facebookScraping = true;
    toggleScrapingControls(true);
    fetch('/scrape/facebook', {
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

function isValidFacebookUrl(url) {
    return /^(https?:\/\/)?(www\.)?facebook\.com\/.+/.test(url);
}