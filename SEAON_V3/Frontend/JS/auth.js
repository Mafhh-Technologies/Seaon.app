/**
 * Authentication Module - Handles user login, logout, session management
 * Uses localStorage for session persistence (in production, use httpOnly cookies)
 */

const Auth = {
    /**
     * Current user data
     */
    user: null,
    
    /**
     * Check if user is authenticated
     * @returns {boolean} True if user has valid token
     */
    isAuthenticated() {
        const token = localStorage.getItem('auth_token');
        const user = localStorage.getItem('auth_user');
        return !!(token && user);
    },
    
    /**
     * Get current user from localStorage
     * @returns {Object|null} User object or null
     */
    getCurrentUser() {
        const userData = localStorage.getItem('auth_user');
        if (userData) {
            try {
                this.user = JSON.parse(userData);
                return this.user;
            } catch (e) {
                return null;
            }
        }
        return null;
    },
    
    /**
     * Login user - in production, this would call the API
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} User data
     */
    async login(email, password) {
        // --- MOCK LOGIN (remove this block and use real API in production) ---
        // For demo purposes, accept any credentials with proper format
        if (email && password && password.length >= 6) {
            const user = {
                id: 1,
                name: email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1),
                email: email,
                role: 'admin',
                avatar: `https://ui-avatars.com/api/?name=${email.split('@')[0]}&background=4F46E5&color=fff`,
            };
            
            // Store session
            localStorage.setItem('auth_token', 'mock_token_' + Date.now());
            localStorage.setItem('auth_user', JSON.stringify(user));
            this.user = user;
            
            return user;
        }
        
        // Real API call (uncomment when backend is ready)
        /*
        try {
            const response = await API.auth.login(email, password);
            const { user, token } = response;
            
            // Store token and user data
            localStorage.setItem('auth_token', token);
            localStorage.setItem('auth_user', JSON.stringify(user));
            this.user = user;
            
            return user;
        } catch (error) {
            console.error('Login failed:', error);
            throw new Error('Invalid email or password');
        }
        */
        
        return null;
    },
    
    /**
     * Logout user - clear session
     */
    async logout() {
        try {
            // Call logout API (optional)
            // await API.auth.logout();
        } catch (e) {
            // Ignore errors on logout
        }
        
        // Clear local session
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        this.user = null;
        
        // Dispatch logout event for other modules
        window.dispatchEvent(new CustomEvent('auth:logout'));
    },
    
    /**
     * Refresh user session (re-validate token)
     * @returns {Promise<Object>} Fresh user data
     */
    async refreshSession() {
        try {
            // In production, call API to refresh token
            // const response = await API.auth.me();
            // const user = response.user;
            
            // For mock, just return current user
            return this.getCurrentUser();
        } catch (error) {
            console.error('Session refresh failed:', error);
            // If refresh fails, logout
            await this.logout();
            throw error;
        }
    },
    
    /**
     * Check if user has specific role
     * @param {string|Array} roles - Role or array of roles to check
     * @returns {boolean} True if user has required role
     */
    hasRole(roles) {
        const user = this.getCurrentUser();
        if (!user) return false;
        
        const userRole = user.role || 'user';
        const allowedRoles = Array.isArray(roles) ? roles : [roles];
        return allowedRoles.includes(userRole);
    },
    
    /**
     * Redirect to login if not authenticated
     * @param {string} redirectUrl - URL to redirect after login
     */
    requireAuth(redirectUrl = '/login.html') {
        if (!this.isAuthenticated()) {
            const currentPath = window.location.pathname;
            const encodedReturn = encodeURIComponent(currentPath);
            window.location.href = `${redirectUrl}?return=${encodedReturn}`;
            return false;
        }
        return true;
    },
};

// Auto-check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    // If we're on a protected page and not authenticated, redirect
    const protectedPages = ['index.html', 'dashboard.html'];
    const currentPage = window.location.pathname.split('/').pop() || '';
    
    if (protectedPages.includes(currentPage) || currentPage === '') {
        Auth.requireAuth();
    }
});