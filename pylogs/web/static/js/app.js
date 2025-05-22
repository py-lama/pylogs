/**
 * PyLogs Viewer JavaScript
 * Enhanced version with real-time updates and improved UI
 */

// State management
const state = {
    currentPage: 1,
    pageSize: 100,
    filters: {
        level: '',
        component: '',
        search: '',
        startDate: '',
        endDate: ''
    },
    totalLogs: 0,
    totalPages: 0,
    autoRefresh: false,
    refreshInterval: null,
    refreshRate: 5000, // 5 seconds
    darkMode: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
    lastLogId: 0 // Track the last log ID for real-time updates
};

// DOM elements
const elements = {
    logsTableBody: document.getElementById('logs-table-body'),
    pagination: document.getElementById('pagination'),
    paginationInfo: document.getElementById('pagination-info'),
    filterForm: document.getElementById('filter-form'),
    levelFilter: document.getElementById('level-filter'),
    componentFilter: document.getElementById('component-filter'),
    searchFilter: document.getElementById('search'),
    startDateFilter: document.getElementById('start-date'),
    endDateFilter: document.getElementById('end-date'),
    resetFiltersBtn: document.getElementById('reset-filters'),
    pageSizeSelect: document.getElementById('page-size'),
    refreshLogsBtn: document.getElementById('refresh-logs'),
    autoRefreshBtn: document.getElementById('auto-refresh'),
    autoRefreshIndicator: document.getElementById('auto-refresh-indicator'),
    darkModeToggle: document.getElementById('dark-mode-toggle'),
    statsLink: document.getElementById('stats-link'),
    statsPanel: document.getElementById('stats-panel'),
    levelStats: document.getElementById('level-stats'),
    componentStats: document.getElementById('component-stats'),
    dateRangeStats: document.getElementById('date-range-stats'),
    totalLogsStats: document.getElementById('total-logs'),
    logDetailModal: new bootstrap.Modal(document.getElementById('log-detail-modal')),
    exportLogsBtn: document.getElementById('export-logs'),
    notificationArea: document.getElementById('notification-area')
};

// Initialize the application
async function init() {
    // Apply dark mode if needed
    if (state.darkMode) {
        document.body.classList.add('dark-mode');
        if (elements.darkModeToggle) {
            elements.darkModeToggle.checked = true;
        }
    }
    
    // Load initial data
    try {
        await Promise.all([
            loadLogs(),
            loadLevels(),
            loadComponents(),
            loadStats()
        ]);
        
        // Show success notification
        showNotification('PyLogs viewer initialized successfully', 'success');
    } catch (error) {
        showNotification('Failed to initialize PyLogs viewer: ' + error.message, 'error');
    }

    // Set up event listeners
    setupEventListeners();
}

// Load logs from the API
async function loadLogs() {
    try {
        const params = new URLSearchParams({
            page: state.currentPage,
            page_size: state.pageSize
        });

        // Add filters if they are set
        if (state.filters.level) params.append('level', state.filters.level);
        if (state.filters.component) params.append('component', state.filters.component);
        if (state.filters.search) params.append('search', state.filters.search);
        if (state.filters.startDate) params.append('start_date', state.filters.startDate);
        if (state.filters.endDate) params.append('end_date', state.filters.endDate);

        const response = await fetch(`/api/logs?${params.toString()}`);
        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Update state
        state.totalLogs = data.total;
        state.totalPages = data.pages;

        // Render logs
        renderLogs(data.logs);
        renderPagination();
        updatePaginationInfo();
    } catch (error) {
        showError(`Failed to load logs: ${error.message}`);
    }
}

// Load available log levels
async function loadLevels() {
    try {
        const response = await fetch('/api/levels');
        const levels = await response.json();

        // Clear existing options except the first one
        while (elements.levelFilter.options.length > 1) {
            elements.levelFilter.remove(1);
        }

        // Add new options
        levels.forEach(level => {
            const option = document.createElement('option');
            option.value = level;
            option.textContent = level;
            elements.levelFilter.appendChild(option);
        });
    } catch (error) {
        showError(`Failed to load log levels: ${error.message}`);
    }
}

// Load available components
async function loadComponents() {
    try {
        const response = await fetch('/api/components');
        const components = await response.json();

        // Clear existing options except the first one
        while (elements.componentFilter.options.length > 1) {
            elements.componentFilter.remove(1);
        }

        // Add new options
        components.forEach(component => {
            const option = document.createElement('option');
            option.value = component;
            option.textContent = component;
            elements.componentFilter.appendChild(option);
        });
    } catch (error) {
        showError(`Failed to load components: ${error.message}`);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        if (stats.error) {
            showError(stats.error);
            return;
        }

        renderStats(stats);
    } catch (error) {
        showError(`Failed to load statistics: ${error.message}`);
    }
}

// Render logs in the table
function renderLogs(logs) {
    elements.logsTableBody.innerHTML = '';

    if (logs.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="5" class="text-center">No logs found</td>`;
        elements.logsTableBody.appendChild(row);
        return;
    }

    logs.forEach(log => {
        const row = document.createElement('tr');
        
        // Format timestamp
        const timestamp = new Date(log.timestamp);
        const formattedTimestamp = timestamp.toLocaleString();
        
        // Create level badge
        const levelBadge = `<span class="level-badge level-${log.level.toLowerCase()}">${log.level}</span>`;
        
        // Truncate message
        const truncatedMessage = `<div class="message-truncate">${escapeHtml(log.message)}</div>`;
        
        row.innerHTML = `
            <td>${formattedTimestamp}</td>
            <td>${levelBadge}</td>
            <td>${log.logger_name}</td>
            <td>${truncatedMessage}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-log" data-log-id="${log.id}">
                    View
                </button>
            </td>
        `;
        
        elements.logsTableBody.appendChild(row);
    });

    // Add event listeners to view buttons
    document.querySelectorAll('.view-log').forEach(button => {
        button.addEventListener('click', () => {
            const logId = button.getAttribute('data-log-id');
            viewLogDetail(logId);
        });
    });
}

// Render pagination controls
function renderPagination() {
    const paginationElement = document.querySelector('#pagination ul');
    paginationElement.innerHTML = '';

    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${state.currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" data-page="${state.currentPage - 1}">Previous</a>`;
    paginationElement.appendChild(prevLi);

    // Page numbers
    const startPage = Math.max(1, state.currentPage - 2);
    const endPage = Math.min(state.totalPages, startPage + 4);

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === state.currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        paginationElement.appendChild(li);
    }

    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${state.currentPage === state.totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" data-page="${state.currentPage + 1}">Next</a>`;
    paginationElement.appendChild(nextLi);

    // Add event listeners to pagination links
    document.querySelectorAll('#pagination .page-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = parseInt(link.getAttribute('data-page'));
            if (page >= 1 && page <= state.totalPages) {
                state.currentPage = page;
                loadLogs();
            }
        });
    });
}

// Update pagination info text
function updatePaginationInfo() {
    const start = (state.currentPage - 1) * state.pageSize + 1;
    const end = Math.min(state.currentPage * state.pageSize, state.totalLogs);
    elements.paginationInfo.textContent = `Showing ${start}-${end} of ${state.totalLogs} logs`;
}

// Render statistics
function renderStats(stats) {
    // Level stats
    elements.levelStats.innerHTML = '';
    Object.entries(stats.level_counts).forEach(([level, count]) => {
        const div = document.createElement('div');
        div.className = 'stat-item';
        div.innerHTML = `
            <span class="stat-label">${level}</span>
            <span class="stat-value">
                <span class="level-badge level-${level.toLowerCase()}">${count}</span>
            </span>
        `;
        elements.levelStats.appendChild(div);
    });

    // Component stats
    elements.componentStats.innerHTML = '';
    Object.entries(stats.component_counts).forEach(([component, count]) => {
        const div = document.createElement('div');
        div.className = 'stat-item';
        div.innerHTML = `
            <span class="stat-label">${component}</span>
            <span class="stat-value">${count}</span>
        `;
        elements.componentStats.appendChild(div);
    });

    // Date range stats
    elements.dateRangeStats.innerHTML = '';
    if (stats.date_range.min_date && stats.date_range.max_date) {
        const minDate = new Date(stats.date_range.min_date).toLocaleString();
        const maxDate = new Date(stats.date_range.max_date).toLocaleString();
        const div = document.createElement('div');
        div.innerHTML = `<div>${minDate} to ${maxDate}</div>`;
        elements.dateRangeStats.appendChild(div);
    } else {
        elements.dateRangeStats.innerHTML = '<div>No logs available</div>';
    }

    // Total logs
    elements.totalLogsStats.innerHTML = `<div class="fw-bold">${stats.total}</div>`;
}

// View log detail
async function viewLogDetail(logId) {
    try {
        const response = await fetch(`/api/log/${logId}`);
        const log = await response.json();

        if (log.error) {
            showError(log.error);
            return;
        }

        // Populate modal with log details
        document.getElementById('detail-id').textContent = log.id;
        document.getElementById('detail-timestamp').textContent = new Date(log.timestamp).toLocaleString();
        document.getElementById('detail-level').innerHTML = `<span class="level-badge level-${log.level.toLowerCase()}">${log.level}</span>`;
        document.getElementById('detail-component').textContent = log.logger_name;
        document.getElementById('detail-thread').textContent = log.thread_name || 'N/A';
        document.getElementById('detail-process').textContent = log.process_name || 'N/A';
        document.getElementById('detail-file').textContent = log.file_path || 'N/A';
        document.getElementById('detail-line').textContent = log.line_number || 'N/A';
        document.getElementById('detail-message').textContent = log.message;
        
        // Format context as JSON if it's an object
        let contextContent = log.context || '{}';
        try {
            if (typeof contextContent === 'string') {
                contextContent = JSON.parse(contextContent);
            }
            document.getElementById('detail-context').textContent = JSON.stringify(contextContent, null, 2);
        } catch (e) {
            document.getElementById('detail-context').textContent = contextContent;
        }

        // Show the modal
        elements.logDetailModal.show();
    } catch (error) {
        showError(`Failed to load log details: ${error.message}`);
    }
}

// Set up event listeners
function setupEventListeners() {
    // Filter form submission
    elements.filterForm.addEventListener('submit', event => {
        event.preventDefault();
        state.filters.level = elements.levelFilter.value;
        state.filters.component = elements.componentFilter.value;
        state.filters.search = elements.searchFilter.value;
        state.filters.startDate = elements.startDateFilter.value;
        state.filters.endDate = elements.endDateFilter.value;
        state.currentPage = 1;
        loadLogs();
    });

    // Reset filters
    elements.resetFiltersBtn.addEventListener('click', () => {
        elements.levelFilter.value = '';
        elements.componentFilter.value = '';
        elements.searchFilter.value = '';
        elements.startDateFilter.value = '';
        elements.endDateFilter.value = '';
        state.filters.level = '';
        state.filters.component = '';
        state.filters.search = '';
        state.filters.startDate = '';
        state.filters.endDate = '';
        state.currentPage = 1;
        loadLogs();
    });

    // Page size change
    elements.pageSizeSelect.addEventListener('change', () => {
        state.pageSize = parseInt(elements.pageSizeSelect.value);
        state.currentPage = 1;
        loadLogs();
    });

    // Refresh logs
    elements.refreshLogsBtn.addEventListener('click', () => {
        loadLogs();
    });

    // Auto-refresh toggle
    if (elements.autoRefreshBtn) {
        elements.autoRefreshBtn.addEventListener('change', () => {
            toggleAutoRefresh(elements.autoRefreshBtn.checked);
        });
    }

    // Dark mode toggle
    if (elements.darkModeToggle) {
        elements.darkModeToggle.addEventListener('change', () => {
            toggleDarkMode(elements.darkModeToggle.checked);
        });
    }

    // Export logs
    if (elements.exportLogsBtn) {
        elements.exportLogsBtn.addEventListener('click', (event) => {
            event.preventDefault();
            exportLogs();
        });
    }

    // Stats link
    elements.statsLink.addEventListener('click', event => {
        event.preventDefault();
        elements.statsPanel.style.display = elements.statsPanel.style.display === 'none' ? 'block' : 'none';
        loadStats();
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        // Ctrl+R to refresh logs
        if (event.ctrlKey && event.key === 'r') {
            event.preventDefault();
            loadLogs();
        }
        // Ctrl+D to toggle dark mode
        if (event.ctrlKey && event.key === 'd') {
            event.preventDefault();
            if (elements.darkModeToggle) {
                elements.darkModeToggle.checked = !elements.darkModeToggle.checked;
                toggleDarkMode(elements.darkModeToggle.checked);
            }
        }
    });
}

// Helper function to show error messages
function showError(message) {
    console.error(message);
    alert(`Error: ${message}`);
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
