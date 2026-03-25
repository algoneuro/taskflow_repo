const API_URL = 'http://127.0.0.1:8000';
let currentToken = null;
let currentUser = null;
let allTasks = [];

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        currentToken = token;
        checkAuth();
    }
    
    // Обработчики форм
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');
    const createTaskForm = document.getElementById('create-task-form');
    
    if (registerForm) registerForm.addEventListener('submit', register);
    if (loginForm) loginForm.addEventListener('submit', login);
    if (createTaskForm) createTaskForm.addEventListener('submit', createTask);
    
    // Валидация в реальном времени
    const regPassword = document.getElementById('reg-password');
    const regUsername = document.getElementById('reg-username');
    const taskTitle = document.getElementById('task-title');
    
    if (regPassword) regPassword.addEventListener('input', validatePassword);
    if (regUsername) regUsername.addEventListener('input', validateUsername);
    if (taskTitle) taskTitle.addEventListener('input', validateTaskTitle);
});

// Валидация
function validatePassword() {
    const password = document.getElementById('reg-password');
    const errorDiv = document.getElementById('reg-error');
    if (!password || !errorDiv) return true;
    
    if (password.value.length > 0 && password.value.length < 6) {
        errorDiv.textContent = '❌ Пароль должен быть не менее 6 символов';
        errorDiv.style.display = 'block';
        return false;
    } else if (password.value.length > 72) {
        errorDiv.textContent = '❌ Пароль не может быть длиннее 72 символов';
        errorDiv.style.display = 'block';
        return false;
    } else {
        errorDiv.style.display = 'none';
        return true;
    }
}

function validateUsername() {
    const username = document.getElementById('reg-username');
    const errorDiv = document.getElementById('reg-error');
    if (!username || !errorDiv) return true;
    
    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    
    if (username.value.length > 0 && username.value.length < 3) {
        errorDiv.textContent = '❌ Имя пользователя должно быть не менее 3 символов';
        errorDiv.style.display = 'block';
        return false;
    } else if (username.value.length > 50) {
        errorDiv.textContent = '❌ Имя пользователя не может быть длиннее 50 символов';
        errorDiv.style.display = 'block';
        return false;
    } else if (username.value.length > 0 && !usernameRegex.test(username.value)) {
        errorDiv.textContent = '❌ Имя пользователя может содержать только буквы, цифры и _';
        errorDiv.style.display = 'block';
        return false;
    } else {
        errorDiv.style.display = 'none';
        return true;
    }
}

function validateTaskTitle() {
    const title = document.getElementById('task-title');
    const errorDiv = document.getElementById('task-error');
    if (!title || !errorDiv) return true;
    
    if (title.value.length > 200) {
        errorDiv.textContent = '❌ Название задачи не может быть длиннее 200 символов';
        errorDiv.style.display = 'block';
        return false;
    } else {
        errorDiv.style.display = 'none';
        return true;
    }
}

// Аутентификация
async function register(e) {
    e.preventDefault();
    if (!validatePassword() || !validateUsername()) return;
    
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    const errorDiv = document.getElementById('reg-error');
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, username, password})
        });
        
        if (response.ok) {
            errorDiv.className = 'success-message';
            errorDiv.textContent = '✅ Регистрация успешна! Теперь войдите.';
            errorDiv.style.display = 'block';
            document.getElementById('register-form').reset();
            setTimeout(() => {
                closeModals();
                showLoginModal();
            }, 2000);
        } else {
            const error = await response.json();
            errorDiv.className = 'error-message';
            errorDiv.textContent = '❌ ' + (error.detail || 'Ошибка регистрации');
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.className = 'error-message';
        errorDiv.textContent = '❌ Ошибка соединения с сервером';
        errorDiv.style.display = 'block';
    }
}

async function login(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            closeModals();
            await loadDashboard();
        } else {
            const error = await response.json();
            errorDiv.className = 'error-message';
            errorDiv.textContent = '❌ ' + (error.detail || 'Неверный email или пароль');
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.className = 'error-message';
        errorDiv.textContent = '❌ Ошибка соединения с сервером';
        errorDiv.style.display = 'block';
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            currentUser = await response.json();
            await loadDashboard();
        } else {
            logout();
        }
    } catch (error) {
        logout();
    }
}

async function loadDashboard() {
    // Скрываем лендинг, показываем дашборд
    const mainContent = document.querySelector('main');
    const appContainer = document.getElementById('app-container');
    
    if (mainContent) mainContent.style.display = 'none';
    if (appContainer) {
        appContainer.style.display = 'block';
        appContainer.innerHTML = await fetchDashboardHTML();
    }
    
    // Обновляем навигацию
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    const userNameSpan = document.getElementById('user-name');
    
    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) {
        userMenu.style.display = 'flex';
        if (userNameSpan && currentUser) {
            userNameSpan.textContent = currentUser.username;
        }
    }
    
    await loadTasks();
    await loadStatistics();
}

async function fetchDashboardHTML() {
    const response = await fetch('dashboard.html');
    return await response.text();
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            allTasks = await response.json();
            displayTasks(allTasks);
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks) {
    const tasksList = document.getElementById('tasks-list');
    if (!tasksList) return;
    
    const filter = document.getElementById('status-filter');
    const filterValue = filter ? filter.value : 'all';
    
    let filteredTasks = tasks;
    if (filterValue !== 'all') {
        filteredTasks = tasks.filter(t => t.status === filterValue);
    }
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<div class="empty-state">📭 Нет задач. Создайте первую задачу!</div>';
        return;
    }
    
    tasksList.innerHTML = filteredTasks.map(task => `
        <div class="task-item" data-task-id="${task.id}">
            <div class="task-title">${escapeHtml(task.title)}</div>
            <div class="task-description">${escapeHtml(task.description || '📝 Нет описания')}</div>
            <div class="task-meta">
                <span>🎯 ${getPriorityText(task.priority)}</span>
                <span>📅 ${new Date(task.created_at).toLocaleDateString()}</span>
                <span>🏷️ ${getStatusText(task.status)}</span>
            </div>
            <div class="task-actions">
                <button onclick="updateTaskStatus(${task.id}, '${task.status === 'completed' ? 'pending' : 'completed'}')" 
                        class="btn-primary complete-btn">
                    ${task.status === 'completed' ? '↺ Вернуть' : '✓ Выполнить'}
                </button>
                <button onclick="deleteTask(${task.id})" class="delete-btn">🗑 Удалить</button>
            </div>
        </div>
    `).join('');
}

function filterTasks() {
    displayTasks(allTasks);
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_URL}/statistics/tasks-summary`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            const stats = await response.json();
            updateStatisticsUI(stats);
        }
        
        const priorityResponse = await fetch(`${API_URL}/statistics/priority-distribution`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (priorityResponse.ok) {
            const priorityStats = await priorityResponse.json();
            updatePriorityUI(priorityStats);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function updateStatisticsUI(stats) {
    const totalEl = document.getElementById('stat-total');
    const completedEl = document.getElementById('stat-completed');
    const progressEl = document.getElementById('stat-progress');
    const priorityEl = document.getElementById('stat-priority');
    const scoreEl = document.getElementById('stat-score');
    
    if (totalEl) totalEl.textContent = stats.total;
    if (completedEl) completedEl.textContent = stats.by_status.completed;
    if (progressEl) progressEl.textContent = `${stats.completion_rate}%`;
    if (priorityEl) priorityEl.textContent = stats.avg_priority;
    if (scoreEl) scoreEl.textContent = stats.workload_score;
}

function updatePriorityUI(priorityStats) {
    const barLow = document.getElementById('bar-low');
    const barMedium = document.getElementById('bar-medium');
    const barHigh = document.getElementById('bar-high');
    const percentLow = document.getElementById('percent-low');
    const percentMedium = document.getElementById('percent-medium');
    const percentHigh = document.getElementById('percent-high');
    
    if (barLow) barLow.style.setProperty('--width', `${priorityStats.percentages.low}%`);
    if (barMedium) barMedium.style.setProperty('--width', `${priorityStats.percentages.medium}%`);
    if (barHigh) barHigh.style.setProperty('--width', `${priorityStats.percentages.high}%`);
    
    // Обновляем проценты
    if (percentLow) percentLow.textContent = `${priorityStats.percentages.low}%`;
    if (percentMedium) percentMedium.textContent = `${priorityStats.percentages.medium}%`;
    if (percentHigh) percentHigh.textContent = `${priorityStats.percentages.high}%`;
    
    // Обновляем ширину баров (динамически)
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width) {
            bar.style.setProperty('--width', `${width}%`);
        }
    });
}

async function createTask(e) {
    e.preventDefault();
    if (!validateTaskTitle()) return;
    
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-desc').value;
    const priority = parseInt(document.getElementById('task-priority').value);
    const errorDiv = document.getElementById('task-error');
    
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({title, description, priority})
        });
        
        if (response.ok) {
            closeCreateTaskModal();
            document.getElementById('create-task-form').reset();
            await loadTasks();
            await loadStatistics();
        } else {
            const error = await response.json();
            errorDiv.className = 'error-message';
            errorDiv.textContent = '❌ ' + (error.detail || 'Ошибка создания задачи');
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.className = 'error-message';
        errorDiv.textContent = '❌ Ошибка соединения с сервером';
        errorDiv.style.display = 'block';
    }
}

window.updateTaskStatus = async function(taskId, status) {
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({status})
        });
        
        if (response.ok) {
            await loadTasks();
            await loadStatistics();
        }
    } catch (error) {
        alert('Ошибка обновления статуса');
    }
}

window.deleteTask = async function(taskId) {
    if (!confirm('🗑 Удалить задачу?')) return;
    
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            await loadTasks();
            await loadStatistics();
        }
    } catch (error) {
        alert('Ошибка удаления задачи');
    }
}

function showLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) modal.style.display = 'flex';
}

function showRegisterModal() {
    const modal = document.getElementById('register-modal');
    if (modal) modal.style.display = 'flex';
}

function showCreateTaskModal() {
    const modal = document.getElementById('create-task-modal');
    if (modal) modal.style.display = 'flex';
}

function closeModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => modal.style.display = 'none');
}

function closeCreateTaskModal() {
    const modal = document.getElementById('create-task-modal');
    if (modal) modal.style.display = 'none';
}

function switchToLogin() {
    closeModals();
    showLoginModal();
}

function switchToRegister() {
    closeModals();
    showRegisterModal();
}

function showDashboard() {
    const tasksSection = document.getElementById('tasks-section');
    const statsSection = document.getElementById('statistics-section');
    if (tasksSection) tasksSection.style.display = 'block';
    if (statsSection) statsSection.style.display = 'none';
}

function showStatistics() {
    const tasksSection = document.getElementById('tasks-section');
    const statsSection = document.getElementById('statistics-section');
    if (tasksSection) tasksSection.style.display = 'none';
    if (statsSection) statsSection.style.display = 'block';
    loadStatistics();
}

function logout() {
    localStorage.removeItem('token');
    currentToken = null;
    currentUser = null;
    
    // Показываем лендинг
    const mainContent = document.querySelector('main');
    const appContainer = document.getElementById('app-container');
    
    if (mainContent) mainContent.style.display = 'block';
    if (appContainer) appContainer.style.display = 'none';
    
    // Обновляем навигацию
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');
    
    if (authButtons) authButtons.style.display = 'flex';
    if (userMenu) userMenu.style.display = 'none';
    
    closeModals();
}

function getPriorityText(priority) {
    const priorities = {1: '🟢 Низкий', 2: '🟡 Средний', 3: '🔴 Высокий'};
    return priorities[priority] || 'Средний';
}

function getStatusText(status) {
    const statuses = {
        'pending': '⏳ Ожидает',
        'in_progress': '🔄 В работе',
        'completed': '✅ Выполнена'
    };
    return statuses[status] || status;
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

// Добавляем стили для баров
const style = document.createElement('style');
style.textContent = `
    .bar {
        position: relative;
    }
    .bar::after {
        width: var(--width, 0%);
    }
`;
document.head.appendChild(style);