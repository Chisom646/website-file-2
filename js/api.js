// API Service Module
// Handles all API calls with authentication, error handling, and JSON parsing

const API_BASE_URL = 'http://localhost:8888/api';

class API {
    // Helper to get auth headers
    static getAuthHeaders() {
        const token = localStorage.getItem('auth_token');
        return {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };
    }

    // Generic request handler
    static async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                return {
                    success: false,
                    error: data.detail || 'Request failed',
                    status: response.status
                };
            }

            return { success: true, data };
        } catch (error) {
            console.error('API request error:', error);
            return {
                success: false,
                error: 'Network error. Please check your connection.'
            };
        }
    }

    // Auth endpoints
    static async login(username, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    static async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    static async getProfile() {
        return this.request('/auth/profile');
    }

    static async updateLanguage(language) {
        return this.request('/auth/language', {
            method: 'PUT',
            body: JSON.stringify({ language })
        });
    }

    // Communities endpoints
    static async getCommunities() {
        return this.request('/communities');
    }

    static async joinCommunity(communityId) {
        return this.request(`/communities/${communityId}/join`, {
            method: 'POST'
        });
    }

    static async leaveCommunity(communityId) {
        return this.request(`/communities/${communityId}/leave`, {
            method: 'POST'
        });
    }

    static async getCommunityMessages(communityId, limit = 50) {
        return this.request(`/communities/${communityId}/messages?limit=${limit}`);
    }

    // Feed endpoints
    static async getPosts(communityId = null, limit = 50) {
        const query = new URLSearchParams();
        if (communityId) query.append('community_id', communityId);
        query.append('limit', limit);
        return this.request(`/posts?${query}`);
    }

    static async createPost(content, communityId = null) {
        return this.request('/posts', {
            method: 'POST',
            body: JSON.stringify({ content, community_id: communityId })
        });
    }

    static async deletePost(postId) {
        return this.request(`/posts/${postId}`, {
            method: 'DELETE'
        });
    }
}

// Export to global scope
window.API = API;
