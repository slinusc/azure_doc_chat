// Utility functions for the RAG Chatbot

/**
 * Format file size in human-readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format timestamp to readable format
 * @param {Date} date - Date object
 * @returns {string} Formatted timestamp
 */
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show a temporary notification message
 * @param {string} message - Message to display
 * @param {string} type - Message type ('success', 'error', 'info')
 * @param {number} duration - Duration in milliseconds (default: 3000)
 */
function showNotification(message, type = 'info', duration = 3000) {
    const statusEl = document.getElementById('uploadStatus');
    statusEl.textContent = message;
    statusEl.className = `upload-status ${type}`;

    if (duration > 0) {
        setTimeout(() => {
            statusEl.className = 'upload-status';
            statusEl.textContent = '';
        }, duration);
    }
}

/**
 * Create a loading spinner element
 * @returns {HTMLElement} Spinner element
 */
function createLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    return spinner;
}

/**
 * Validate file type (PDF only)
 * @param {File} file - File to validate
 * @returns {boolean} True if file is a PDF
 */
function isValidFileType(file) {
    return file.name.toLowerCase().endsWith('.pdf');
}

/**
 * Debounce function to limit function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Check if element is scrolled to bottom
 * @param {HTMLElement} element - Element to check
 * @param {number} threshold - Threshold in pixels (default: 10)
 * @returns {boolean} True if scrolled to bottom
 */
function isScrolledToBottom(element, threshold = 10) {
    return element.scrollHeight - element.clientHeight - element.scrollTop <= threshold;
}

/**
 * Scroll element to bottom
 * @param {HTMLElement} element - Element to scroll
 */
function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}
