// API Base URL
const API_BASE_URL = 'http://localhost:8888/api';

// Authentication functions
class AuthService {
    // Store token in localStorage
    static setToken(token) {
        localStorage.setItem('auth_token', token);
    }

    // Get token from localStorage
    static getToken() {
        return localStorage.getItem('auth_token');
    }

    // Remove token from localStorage
    static removeToken() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
    }

    // Check if user is authenticated
    static isAuthenticated() {
        return !!this.getToken();
    }

    // Store user data
    static setUserData(userData) {
        localStorage.setItem('user_data', JSON.stringify(userData));
    }

    // Get user data
    static getUserData() {
        const data = localStorage.getItem('user_data');
        return data ? JSON.parse(data) : null;
    }

    // Clear all auth data
    static logout() {
        this.removeToken();
        localStorage.removeItem('user_data');
    }

    // Validate email format
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Validate phone number format
    static validatePhone(phone) {
        const re = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
        return re.test(phone);
    }

    // Format date to YYYY-MM-DD
    static formatDate(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // NEW: Calculate byte length of a string
    static getStringByteLength(str) {
        return new TextEncoder().encode(str).length;
    }
}

// API Service
class ApiService {
    // Login user
    static async login(username, password) {
        try {
            // Check password byte length before sending
            const passwordBytes = AuthService.getStringByteLength(password);
            if (passwordBytes > 72) {
                return {
                    success: false,
                    error: `Password is ${passwordBytes} bytes long (max 72 bytes). Please use a shorter password.`
                };
            }
            
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                AuthService.setToken(data.access_token);
                AuthService.setUserData({
                    user_id: data.user_id,
                    username: data.username,
                    email: data.email,
                    name: data.name,
                    roles: data.roles
                });
                return { success: true, data: data };
            } else {
                return { 
                    success: false, 
                    error: data.detail || 'Invalid username or password' 
                };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { 
                success: false, 
                error: 'Network error. Please try again.' 
            };
        }
    }

    // Register user
    static async register(userData) {
        try {
            // Check password byte length before sending
            const passwordBytes = AuthService.getStringByteLength(userData.password);
            if (passwordBytes > 72) {
                return {
                    success: false,
                    error: `Password is ${passwordBytes} bytes long (max 72 bytes). Please use a shorter password.`
                };
            }
            
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            
            if (response.ok) {
                return { success: true, data: data };
            } else {
                // Extract error message from FastAPI response
                let errorMessage = 'Registration failed';
                if (data.detail) {
                    if (typeof data.detail === 'string') {
                        errorMessage = data.detail;
                    } else if (typeof data.detail === 'object') {
                        errorMessage = data.detail.message || JSON.stringify(data.detail);
                    }
                }
                return { 
                    success: false, 
                    error: errorMessage
                };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { 
                success: false, 
                error: 'Network error. Please try again.' 
            };
        }
    }

    // Get current user profile
    static async getProfile() {
        const token = AuthService.getToken();
        if (!token) {
            return { success: false, error: 'Not authenticated' };
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/profile`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (response.ok) {
                AuthService.setUserData(data);
                return { success: true, data: data };
            } else {
                return { 
                    success: false, 
                    error: data.detail || 'Failed to fetch profile' 
                };
            }
        } catch (error) {
            console.error('Profile fetch error:', error);
            return { 
                success: false, 
                error: 'Network error. Please try again.' 
            };
        }
    }

    // Check username availability
    static async checkUsername(username) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-username/${username}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            return { success: true, data: data };
        } catch (error) {
            console.error('Username check error:', error);
            return { 
                success: false, 
                error: 'Network error. Please try again.' 
            };
        }
    }

    // Check email availability
    static async checkEmail(email) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-email/${email}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            return { success: true, data: data };
        } catch (error) {
            console.error('Email check error:', error);
            return { 
                success: false, 
                error: 'Network error. Please try again.' 
            };
        }
    }
    
    // NEW: Check password byte length
    static async checkPasswordByteLength(password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-password-length`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password })
            });

            const data = await response.json();
            return { success: true, data: data };
        } catch (error) {
            return { 
                success: false, 
                error: 'Unable to check password length' 
            };
        }
    }
}

// UI Helper functions
class UIHelper {
    static showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.style.color = '#ff0000';
            element.style.display = 'block';
        }
    }

    static hideError(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }

    static showSuccess(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.style.color = '#00aa00';
            element.style.display = 'block';
        }
    }

    static showLoading(button) {
        const originalText = button.textContent;
        button.disabled = true;
        button.innerHTML = '<span class="loading">Loading...</span>';
        return originalText;
    }

    static hideLoading(button, originalText) {
        button.disabled = false;
        button.textContent = originalText;
    }

    static redirect(url) {
        window.location.href = url;
    }

    static showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            `;
            document.body.appendChild(toastContainer);
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
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
            max-width: 350px;
            word-wrap: break-word;
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
    
    // NEW: Update password byte counter display
    static updatePasswordByteCounter(password, counterElementId) {
        const byteLength = AuthService.getStringByteLength(password);
        const counter = document.getElementById(counterElementId);
        
        if (counter) {
            counter.textContent = `${byteLength}/72 bytes`;
            
            if (byteLength > 72) {
                counter.style.color = '#e74c3c';
                counter.style.fontWeight = 'bold';
                counter.className = 'byte-counter danger';
            } else if (byteLength > 60) {
                counter.style.color = '#f39c12';
                counter.style.fontWeight = 'normal';
                counter.className = 'byte-counter warning';
            } else {
                counter.style.color = '#27ae60';
                counter.style.fontWeight = 'normal';
                counter.className = 'byte-counter safe';
            }
        }
        
        return byteLength;
    }
}

// Add CSS for loading, animations, and byte counter
const style = document.createElement('style');
style.textContent = `
    .loading {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .error-message {
        color: #ff0000;
        font-size: 14px;
        margin-top: 5px;
        display: none;
    }
    
    .success-message {
        color: #00aa00;
        font-size: 14px;
        margin-top: 5px;
        display: none;
    }
    
    .byte-counter {
        font-size: 12px;
        margin-top: 5px;
        transition: color 0.3s ease;
    }
    
    .byte-counter.safe {
        color: #27ae60;
    }
    
    .byte-counter.warning {
        color: #f39c12;
    }
    
    .byte-counter.danger {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .password-input-over-limit {
        border-color: #e74c3c !important;
        box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2);
    }
`;
document.head.appendChild(style);

// Export to global scope
window.AuthService = AuthService;
window.ApiService = ApiService;
window.UIHelper = UIHelper;