// Handles Login and Signup

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            window.location.href = '/tractorview';
        } else {
            alert(result.message || 'Login failed');
        }
    } catch (err) {
        console.error('Error during login:', err);
        alert('An error occurred during login.');
    }
}

async function handleSignup(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            alert('Account created successfully. Please login.');
            window.location.href = '/login';
        } else {
            alert(result.message || 'Signup failed');
        }
    } catch (err) {
        console.error('Error during signup:', err);
        alert('An error occurred during signup.');
    }
}

async function handleLogout() {
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

// Attach event listeners based on the current page
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const signupForm = document.getElementById('signup-form');
    if (signupForm) signupForm.addEventListener('submit', handleSignup);
    
    // Find logout links/buttons
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }
});
