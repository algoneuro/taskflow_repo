const API_URL = 'http://127.0.0.1:8000';
let currentToken = null;
let currentUser = null;

// Проверка авторизации
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        if (response.ok) {
            currentToken = token;
            currentUser = await response.json();
            return currentUser;
        } else {
            localStorage.removeItem('token');
            return null;
        }
    } catch (error) {
        return null;
    }
}

// Обновление навбара на главной странице
async function updateIndexNavbar() {
    const user = await checkAuth();
    const unauthDiv = document.getElementById('unauth-buttons');
    const authDiv = document.getElementById('auth-user-info');
    const greetingSpan = document.getElementById('greeting-username');
    const heroButtons = document.getElementById('hero-buttons');
    const heroAuthedButtons = document.getElementById('hero-authed-buttons');
    
    if (user) {
        if (unauthDiv) unauthDiv.style.display = 'none';
        if (authDiv) authDiv.style.display = 'flex';
        if (greetingSpan) greetingSpan.textContent = `👋 ${user.username}`;
        if (heroButtons) heroButtons.style.display = 'none';
        if (heroAuthedButtons) heroAuthedButtons.style.display = 'flex';
    } else {
        if (unauthDiv) unauthDiv.style.display = 'flex';
        if (authDiv) authDiv.style.display = 'none';
        if (heroButtons) heroButtons.style.display = 'flex';
        if (heroAuthedButtons) heroAuthedButtons.style.display = 'none';
    }
}

// Проверка для защищенных страниц (дашборд, детальная)
async function checkAuthAndRedirect() {
    const user = await checkAuth();
    if (!user && !window.location.pathname.includes('index.html') && 
        !window.location.pathname.includes('login.html') && 
        !window.location.pathname.includes('register.html')) {
        window.location.href = 'login.html';
        return false;
    }
    return !!user;
}

function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(elementId, message) {
    const successDiv = document.getElementById(elementId);
    if (successDiv) {
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }
}

function logout() {
    localStorage.removeItem('token');
    currentToken = null;
    currentUser = null;
    window.location.href = 'index.html';
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}