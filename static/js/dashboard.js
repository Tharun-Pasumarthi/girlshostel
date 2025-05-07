document.addEventListener('DOMContentLoaded', function() {
    // Initialize widgets
    initializeWidgets();
    
    // Handle widget refresh
    const refreshButtons = document.querySelectorAll('.refresh-widget');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const widgetId = this.dataset.widgetId;
            refreshWidget(widgetId);
        });
    });
});

function initializeWidgets() {
    const widgets = document.querySelectorAll('.widget');
    widgets.forEach(widget => {
        const widgetId = widget.dataset.widgetId;
        loadWidgetData(widgetId);
    });
}

function loadWidgetData(widgetId) {
    const widgetContent = document.querySelector(`.widget-content[data-widget-id="${widgetId}"]`);
    if (!widgetContent) return;
    
    // Show loading spinner
    widgetContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Fetch widget data
    fetch(`/dashboard/widgets/${widgetId}/data/`)
        .then(response => response.json())
        .then(data => {
            if (data.data) {
                updateWidgetContent(widgetContent, data.data);
            }
        })
        .catch(error => {
            console.error('Error loading widget data:', error);
            widgetContent.innerHTML = `
                <div class="alert alert-danger">
                    Error loading widget data. Please try again.
                </div>
            `;
        });
}

function refreshWidget(widgetId) {
    const refreshButton = document.querySelector(`.refresh-widget[data-widget-id="${widgetId}"]`);
    if (refreshButton) {
        // Add spinning animation
        refreshButton.querySelector('i').classList.add('fa-spin');
        
        // Reload widget data
        loadWidgetData(widgetId);
        
        // Remove spinning animation after a delay
        setTimeout(() => {
            refreshButton.querySelector('i').classList.remove('fa-spin');
        }, 1000);
    }
}

function updateWidgetContent(widgetElement, data) {
    const widgetType = widgetElement.closest('.widget').dataset.widgetType;
    
    switch (widgetType) {
        case 'STATS':
            updateStatsWidget(widgetElement, data);
            break;
        case 'CHART':
            updateChartWidget(widgetElement, data);
            break;
        case 'TABLE':
            updateTableWidget(widgetElement, data);
            break;
        case 'LIST':
            updateListWidget(widgetElement, data);
            break;
        default:
            widgetElement.innerHTML = `
                <div class="alert alert-warning">
                    Unknown widget type: ${widgetType}
                </div>
            `;
    }
}

function updateStatsWidget(widgetElement, data) {
    let html = '<div class="row">';
    
    for (const [key, value] of Object.entries(data)) {
        html += `
            <div class="col">
                <div class="text-center">
                    <h3 class="mb-0">${value}</h3>
                    <p class="text-muted">${key.replace(/_/g, ' ').toUpperCase()}</p>
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    widgetElement.innerHTML = html;
}

function updateChartWidget(widgetElement, data) {
    // This function will be implemented when we add charting library
    widgetElement.innerHTML = `
        <div class="alert alert-info">
            Chart visualization will be implemented soon.
        </div>
    `;
}

function updateTableWidget(widgetElement, data) {
    if (!data.headers || !data.rows) {
        widgetElement.innerHTML = `
            <div class="alert alert-warning">
                Invalid table data format
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        ${data.headers.map(header => `<th>${header}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${data.rows.map(row => `
                        <tr>
                            ${row.map(cell => `<td>${cell}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    widgetElement.innerHTML = html;
}

function updateListWidget(widgetElement, data) {
    if (!Array.isArray(data)) {
        widgetElement.innerHTML = `
            <div class="alert alert-warning">
                Invalid list data format
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group">';
    
    data.forEach(item => {
        html += `
            <a href="${item.url || '#'}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${item.title}</h6>
                    <small>${item.time}</small>
                </div>
                <p class="mb-1">${item.description}</p>
                ${item.badge ? `
                    <small class="text-muted">
                        <span class="badge bg-${item.badge.color}">${item.badge.text}</span>
                    </small>
                ` : ''}
            </a>
        `;
    });
    
    html += '</div>';
    widgetElement.innerHTML = html;
} 