// O:\Flask\scrape\static\js\utils.js
function handleError(error) {
    console.error('Scraping error:', error);
    Swal.fire('Error', `Scraping failed: ${error.message}`, 'error');
    toggleScrapingControls(false);
}

function toggleScrapingControls(scraping) {
    document.getElementById('start-btn').disabled = scraping;
    document.getElementById('stop-btn').disabled = !scraping;
}

function exportData(format) {
    window.location.href = `/export/${format}`;
}