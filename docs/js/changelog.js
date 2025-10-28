// Load and display changelog data

async function loadChangelog() {
    try {
        const response = await fetch('data/changelog.json');
        const data = await response.json();

        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('changelog-content').style.display = 'block';

        // Display period information
        const previousDate = formatDate(data.previous_date);
        const currentDate = formatDate(data.current_date);
        document.getElementById('period-info').textContent =
            `Comparing: ${previousDate} → ${currentDate} (${data.previous_count} → ${data.current_count} datasets)`;

        // Display summary
        document.getElementById('new-count').textContent = data.summary.new_count;
        document.getElementById('removed-count').textContent = data.summary.removed_count;
        document.getElementById('updated-count').textContent = data.summary.updated_count;
        document.getElementById('unchanged-count').textContent = data.summary.unchanged_count;

        // Display new datasets
        if (data.changes.new_datasets.length > 0) {
            document.getElementById('new-datasets-section').style.display = 'block';
            displayNewDatasets(data.changes.new_datasets);
        }

        // Display updated datasets
        if (data.changes.updated_datasets.length > 0) {
            document.getElementById('updated-datasets-section').style.display = 'block';
            displayUpdatedDatasets(data.changes.updated_datasets);
        }

        // Display removed datasets
        if (data.changes.removed_datasets.length > 0) {
            document.getElementById('removed-datasets-section').style.display = 'block';
            displayRemovedDatasets(data.changes.removed_datasets);
        }

    } catch (error) {
        console.error('Changelog loading error:', error);
        document.getElementById('loading').textContent =
            'Changelog not yet available. Data will be collected starting next week.';
    }
}

function formatDate(dateStr) {
    // YYYYMMDD -> YYYY-MM-DD
    return `${dateStr.slice(0,4)}-${dateStr.slice(4,6)}-${dateStr.slice(6,8)}`;
}

function displayNewDatasets(datasets) {
    const container = document.getElementById('new-datasets-list');
    container.innerHTML = '';

    datasets.forEach(dataset => {
        const item = document.createElement('div');
        item.className = 'dataset-item';

        const title = document.createElement('div');
        title.className = 'dataset-title';
        title.innerHTML = `<a href="${dataset.url}" target="_blank">${dataset.id}</a>`;

        const meta = document.createElement('div');
        meta.className = 'dataset-meta';
        meta.textContent = `Author: ${dataset.author || 'Unknown'}`;

        const badges = document.createElement('div');
        badges.style.marginTop = '0.5rem';

        if (dataset.downloads > 0) {
            const downloadBadge = document.createElement('span');
            downloadBadge.className = 'change-badge neutral';
            downloadBadge.textContent = `${dataset.downloads.toLocaleString()} downloads`;
            badges.appendChild(downloadBadge);
        }

        if (dataset.likes > 0) {
            const likeBadge = document.createElement('span');
            likeBadge.className = 'change-badge neutral';
            likeBadge.textContent = `${dataset.likes} likes`;
            badges.appendChild(likeBadge);
        }

        if (dataset.description) {
            const description = document.createElement('div');
            description.className = 'dataset-description';
            description.textContent = dataset.description.substring(0, 200) + (dataset.description.length > 200 ? '...' : '');
            item.appendChild(description);
        }

        item.appendChild(title);
        item.appendChild(meta);
        item.appendChild(badges);
        container.appendChild(item);
    });
}

function displayUpdatedDatasets(datasets) {
    const container = document.getElementById('updated-datasets-list');
    container.innerHTML = '';

    datasets.forEach(dataset => {
        const item = document.createElement('div');
        item.className = 'dataset-item';

        const title = document.createElement('div');
        title.className = 'dataset-title';
        title.innerHTML = `<a href="${dataset.url}" target="_blank">${dataset.id}</a>`;

        const meta = document.createElement('div');
        meta.className = 'dataset-meta';
        meta.textContent = `Author: ${dataset.author || 'Unknown'}`;

        const changes = document.createElement('div');
        changes.style.marginTop = '0.5rem';

        const downloadChange = dataset.changes.downloads.change;
        if (downloadChange !== 0) {
            const badge = document.createElement('span');
            badge.className = `change-badge ${downloadChange > 0 ? 'positive' : 'negative'}`;
            badge.textContent = `Downloads: ${downloadChange > 0 ? '+' : ''}${downloadChange.toLocaleString()} (${dataset.changes.downloads.previous.toLocaleString()} → ${dataset.changes.downloads.current.toLocaleString()})`;
            changes.appendChild(badge);
        }

        const likeChange = dataset.changes.likes.change;
        if (likeChange !== 0) {
            const badge = document.createElement('span');
            badge.className = `change-badge ${likeChange > 0 ? 'positive' : 'negative'}`;
            badge.textContent = `Likes: ${likeChange > 0 ? '+' : ''}${likeChange} (${dataset.changes.likes.previous} → ${dataset.changes.likes.current})`;
            changes.appendChild(badge);
        }

        if (dataset.changes.description_changed) {
            const badge = document.createElement('span');
            badge.className = 'change-badge neutral';
            badge.textContent = 'Description updated';
            changes.appendChild(badge);
        }

        item.appendChild(title);
        item.appendChild(meta);
        item.appendChild(changes);
        container.appendChild(item);
    });
}

function displayRemovedDatasets(datasets) {
    const container = document.getElementById('removed-datasets-list');
    container.innerHTML = '';

    datasets.forEach(dataset => {
        const item = document.createElement('div');
        item.className = 'dataset-item';

        const title = document.createElement('div');
        title.className = 'dataset-title';
        title.innerHTML = `<a href="${dataset.url}" target="_blank">${dataset.id}</a>`;

        const meta = document.createElement('div');
        meta.className = 'dataset-meta';
        meta.textContent = `Author: ${dataset.author || 'Unknown'}`;

        const badges = document.createElement('div');
        badges.style.marginTop = '0.5rem';

        const downloadBadge = document.createElement('span');
        downloadBadge.className = 'change-badge neutral';
        downloadBadge.textContent = `Had ${dataset.downloads.toLocaleString()} downloads`;
        badges.appendChild(downloadBadge);

        const likeBadge = document.createElement('span');
        likeBadge.className = 'change-badge neutral';
        likeBadge.textContent = `Had ${dataset.likes} likes`;
        badges.appendChild(likeBadge);

        if (dataset.description) {
            const description = document.createElement('div');
            description.className = 'dataset-description';
            description.textContent = dataset.description.substring(0, 200) + (dataset.description.length > 200 ? '...' : '');
            item.appendChild(description);
        }

        item.appendChild(title);
        item.appendChild(meta);
        item.appendChild(badges);
        container.appendChild(item);
    });
}

// Execute on page load
document.addEventListener('DOMContentLoaded', loadChangelog);
