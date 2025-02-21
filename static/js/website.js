let collectedData = [];
let isScraping = false;

async function startWebsiteScraping() {
    const url = document.getElementById('website-url').value;
    const elementType = document.getElementById('element-type').value;
    if (!isValidUrl(url)) {
        Swal.fire('Invalid URL', 'Please enter a valid website URL', 'error');
        return;
    }
    isScraping = true;
    toggleScrapingControls(true);
    updateExportOptions();
    const response = await fetch('/scrape/website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, element_type: elementType })
    });
    const data = await response.json();
    if (data.error) {
        Swal.fire('Error', data.error, 'error');
        isScraping = false;
        toggleScrapingControls(false);
        return;
    }
    collectedData = data.data;
    updateProgress();
    isScraping = false;
    toggleScrapingControls(false);
}

function updateProgress() {
    document.getElementById('progress-bar').style.width = '100%';
    const resultsDiv = document.getElementById('results');
    if (collectedData.length > 0 && collectedData[0].endswith('.zip')) {
        resultsDiv.innerHTML = `
            <div class="col-12">
                <div class="card mb-2">
                    <div class="card-body">
                        <a href="#" onclick="exportData('zip')">Download Images (ZIP)</a>
                    </div>
                </div>
            </div>
        `;
    } else {
        resultsDiv.innerHTML = collectedData.map(item => `
            <div class="col-12">
                <div class="card mb-2">
                    <div class="card-body">${item}</div>
                </div>
            </div>
        `).join('');
    }
}

function stopScraping() {
    isScraping = false;
    toggleScrapingControls(false);
}

function isValidUrl(url) {
    return /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}/.test(url);
}

function exportData(format) {
    fetch(`/export/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: collectedData })
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

document.addEventListener('DOMContentLoaded', updateExportOptions);