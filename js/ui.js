// UI Helper Module
// Provides utilities for toast notifications, loading states, and safe rendering

class UI {
    // Show toast notification
    static showToast(message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            `;
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            padding: 15px 20px;
            background: ${type === 'success' ? '#4CAF50' :
                        type === 'error' ? '#f44336' :
                        type === 'warning' ? '#ff9800' : '#2196F3'};
            color: white;
            border-radius: 12px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
            max-width: 350px;
            word-wrap: break-word;
            font-weight: 500;
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // Show loading spinner
    static showLoading(element, message = 'Loading...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (!element) return;

        element.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    // Show empty state
    static showEmpty(element, message, icon = '📭') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (!element) return;

        element.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">${icon}</div>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    // Show error state
    static showError(element, message) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (!element) return;

        element.innerHTML = `
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    // Escape HTML to prevent XSS
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Safely set text content
    static setText(element, text) {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.textContent = text;
        }
    }

    // Format date
    static formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString();
    }

    // Format time
    static formatTime(dateString) {
        return new Date(dateString).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Disable button with loading state
    static disableButton(button, loadingText = 'Loading...') {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return null;

        const originalText = button.textContent;
        button.disabled = true;
        button.classList.add('btn-loading');
        button.textContent = loadingText;
        return originalText;
    }

    // Enable button
    static enableButton(button, originalText) {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return;

        button.disabled = false;
        button.classList.remove('btn-loading');
        if (originalText) {
            button.textContent = originalText;
        }
    }

    // Confirm action
    static confirm(message) {
        return window.confirm(message);
    }

    // Create element with safe content
    static createElement(tag, className, textContent) {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent) el.textContent = textContent;
        return el;
    }
}

// Add required CSS for UI components
const uiStyles = document.createElement('style');
uiStyles.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-spinner {
        text-align: center;
        padding: 40px 20px;
    }

    .spinner {
        width: 40px;
        height: 40px;
        margin: 0 auto 15px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #0066cc;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    .loading-spinner p {
        color: #666;
        margin: 0;
    }

    .empty-state, .error-state {
        text-align: center;
        padding: 60px 20px;
    }

    .empty-icon, .error-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }

    .empty-state p, .error-state p {
        color: #666;
        font-size: 16px;
        margin: 0;
    }

    .error-state p {
        color: #f44336;
    }

    .btn-loading {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;
document.head.appendChild(uiStyles);

// Export to global scope
window.UI = UI;
