// Load and visualize trend data

async function loadTrendData() {
    try {
        const response = await fetch('data/trends.json');
        const data = await response.json();
        const trends = data.trends;

        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('trend-content').style.display = 'block';

        // Display growth rate
        document.getElementById('growth-rate').textContent =
            trends.growth_rate > 0 ? `+${trends.growth_rate}%` : `${trends.growth_rate}%`;
        document.getElementById('total-weeks').textContent = trends.total_weeks;

        // Display date range
        if (trends.first_date && trends.last_date) {
            const firstDate = formatDate(trends.first_date);
            const lastDate = formatDate(trends.last_date);
            document.getElementById('date-range').textContent = `${firstDate} ~ ${lastDate}`;
        }

        // Create charts
        createDatasetsChart(trends);
        createDownloadsChart(trends);
        createLikesChart(trends);
        createMultilingualChart(trends);

    } catch (error) {
        console.error('Trend data loading error:', error);
        document.getElementById('loading').textContent =
            'Trend data not yet available. Data will be collected starting next week.';
    }
}

function formatDate(dateStr) {
    // YYYYMMDD -> YYYY-MM-DD
    return `${dateStr.slice(0,4)}-${dateStr.slice(4,6)}-${dateStr.slice(6,8)}`;
}

function createDatasetsChart(trends) {
    const ctx = document.getElementById('datasetsChart').getContext('2d');

    // Determine chart type based on data points
    const chartType = trends.dates.length === 1 ? 'bar' : 'line';

    new Chart(ctx, {
        type: chartType,
        data: {
            labels: trends.dates.map(formatDate),
            datasets: [{
                label: 'Total Datasets',
                data: trends.total_datasets,
                borderColor: '#ff6b35',
                backgroundColor: chartType === 'bar' ? 'rgba(255, 107, 53, 0.7)' : 'rgba(255, 107, 53, 0.1)',
                tension: 0.4,
                fill: chartType === 'line',
                borderWidth: chartType === 'bar' ? 1 : 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createDownloadsChart(trends) {
    const ctx = document.getElementById('downloadsChart').getContext('2d');

    // Determine chart type based on data points
    const chartType = trends.dates.length === 1 ? 'bar' : 'line';

    new Chart(ctx, {
        type: chartType,
        data: {
            labels: trends.dates.map(formatDate),
            datasets: [{
                label: 'Total Downloads',
                data: trends.total_downloads,
                borderColor: '#004e89',
                backgroundColor: chartType === 'bar' ? 'rgba(0, 78, 137, 0.7)' : 'rgba(0, 78, 137, 0.1)',
                tension: 0.4,
                fill: chartType === 'line',
                borderWidth: chartType === 'bar' ? 1 : 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createLikesChart(trends) {
    const ctx = document.getElementById('likesChart').getContext('2d');

    // Determine chart type based on data points
    const chartType = trends.dates.length === 1 ? 'bar' : 'line';

    new Chart(ctx, {
        type: chartType,
        data: {
            labels: trends.dates.map(formatDate),
            datasets: [{
                label: 'Total Likes',
                data: trends.total_likes,
                borderColor: '#2ecc71',
                backgroundColor: chartType === 'bar' ? 'rgba(46, 204, 113, 0.7)' : 'rgba(46, 204, 113, 0.1)',
                tension: 0.4,
                fill: chartType === 'line',
                borderWidth: chartType === 'bar' ? 1 : 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createMultilingualChart(trends) {
    const ctx = document.getElementById('multilingualChart').getContext('2d');

    // Calculate multilingual ratio
    const multilingualRatio = trends.total_datasets.map((total, index) => {
        const multilingual = trends.multilingual_count[index];
        return total > 0 ? (multilingual / total * 100).toFixed(1) : 0;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trends.dates.map(formatDate),
            datasets: [{
                label: 'Multilingual Dataset Ratio (%)',
                data: multilingualRatio,
                backgroundColor: 'rgba(155, 89, 182, 0.7)',
                borderColor: '#9b59b6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Execute on page load
document.addEventListener('DOMContentLoaded', loadTrendData);
