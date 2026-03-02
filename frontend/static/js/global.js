/**
 * global.js - Shared logic for all Tractent frontend pages
 * Handles: Navbar auth state, footer, and common utilities
 */

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Initialize Navbar and Footer if they exist as skeletons
    await checkAuthStatus();

    // 2. Global Event Listeners
    setupGlobalListeners();
});

async function checkAuthStatus() {
    const authContainer = document.getElementById('auth-nav-container');
    if (!authContainer) return;

    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();

        if (data.logged_in) {
            authContainer.innerHTML = `
                <a href="/profile" class="navbar-nav nav-linkmain" style="font-size: 1rem; font-weight: 700; padding: 6px 0; text-transform: none;">Profile</a>
                <a href="#" id="logout-btn" class="btn-nav-danger">Logout</a>
            `;
            // Re-attach logout listener
            document.getElementById('logout-btn').addEventListener('click', handleLogout);

            // Show owner-only elements if on relevant pages
            document.querySelectorAll('.owner-only').forEach(el => el.style.display = 'block');
        } else {
            authContainer.innerHTML = `
                <a href="/login" class="btn-nav-secondary">Login</a>
                <a href="/signup" class="btn-nav-primary">Sign Up</a>
            `;
            document.querySelectorAll('.owner-only').forEach(el => el.style.display = 'none');
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
    }
}

async function handleLogout(e) {
    if (e) e.preventDefault();
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            window.location.href = '/login';
        }
    } catch (err) {
        console.error('Error during logout:', err);
    }
}

function setupGlobalListeners() {
    // Add any global click handlers here
}
