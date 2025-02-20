let websiteScraping = false;
let pollingInterval;

function startWebsiteScraping() {
    const url = document.getElementById('website-url').value;
    const elementType = document.getElementById('element-type').value;
    if (!isValidUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid website URL', 'error');
        return;
    }
    websiteScraping = true;
    toggleScrapingControls(true);
    updateExportOptions(); // Update export options when scraping starts
    fetch('/scrape/website', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, element_type: elementType })
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
            const resultsDiv = document.getElementById('results');
            if (data.element_type === 'images' && data.comments.length > 0) {
                const zipFile = data.comments[0]; // The zip filename
                resultsDiv.innerHTML = `
                    <div class="col-12">
                        <div class="card mb-2 animate__animated animate__fadeIn">
                            <div class="card-body">
                                <a href="/download/${zipFile}" download>Download Images (ZIP)</a>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                resultsDiv.innerHTML = data.comments.map(comment => `
                    <div class="col-12">
                        <div class="card mb-2 animate__animated animate__fadeIn">
                            <div class="card-body">${comment}</div>
                        </div>
                    </div>
                `).join('');
            }
            if (!data.scraping) {
                clearInterval(pollingInterval);
                toggleScrapingControls(false);
            }
        });
}

function isValidUrl(url) {
    return /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}/.test(url);
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
    websiteScraping = false;
    toggleScrapingControls(false);
}

function updateExportOptions() {
    const elementType = document.getElementById('element-type').value;
    const exportMenu = document.getElementById('export-menu');
    const excelOption = exportMenu.querySelector('li:nth-child(1)');
    const wordOption = exportMenu.querySelector('li:nth-child(2)');
    const zipOption = exportMenu.querySelector('.zip-option');

    if (elementType === 'images') {
        excelOption.style.display = 'none';
        wordOption.style.display = 'none';
        zipOption.style.display = 'block';
    } else {
        excelOption.style.display = 'block';
        wordOption.style.display = 'block';
        zipOption.style.display = 'none';
    }
}

// Call this on page load to set initial state
document.addEventListener('DOMContentLoaded', updateExportOptions);