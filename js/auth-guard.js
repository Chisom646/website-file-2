// Authentication Guard Module
// Handles authentication checks and redirects

class Auth {
    static TOKEN_KEY = 'auth_token';
    static USER_DATA_KEY = 'user_data';

    // Check if user is authenticated
    static isAuthenticated() {
        return !!localStorage.getItem(this.TOKEN_KEY);
    }

    // Get stored token
    static getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    }

    // Store token
    static setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    }

    // Get user data
    static getUserData() {
        const data = localStorage.getItem(this.USER_DATA_KEY);
        return data ? JSON.parse(data) : null;
    }

    // Store user data
    static setUserData(userData) {
        localStorage.setItem(this.USER_DATA_KEY, JSON.stringify(userData));
    }

    // Clear all auth data
    static logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_DATA_KEY);
    }

    // Redirect to login if not authenticated
    static requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    }

    // Initialize auth guard on page load
    static initGuard() {
        const currentPage = window.location.pathname;
        const protectedPages = ['dashboard.html', 'profile.html', 'groups.html', 'communities.html', 'feed.html'];

        if (protectedPages.some(page => currentPage.includes(page))) {
            this.requireAuth();
        }
    }

    // Handle login success
    static handleLoginSuccess(data) {
        this.setToken(data.access_token);
        this.setUserData({
            user_id: data.user_id,
            username: data.username,
            email: data.email,
            name: data.name,
            roles: data.roles
        });
    }
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    Auth.initGuard();
});

// Export to global scope
window.Auth = Auth;
