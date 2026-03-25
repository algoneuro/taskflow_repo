let allTasks = [];

document.addEventListener('DOMContentLoaded', async () => {
    const isAuth = await checkAuthAndRedirect();
    if (!isAuth) return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab === 'stats') {
        showStatistics();
    } else {
        showTasks();
    }
    
    await loadUser();
    await loadTasks();
    await loadStatistics();
});

async function loadUser() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        if (response.ok) {
            currentUser = await response.json();
            const usernameSpan = document.getElementById('username-display');
            if (usernameSpan) {
                usernameSpan.textContent = currentUser.username;
            }
        }
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            allTasks = await response.json();
            displayTasks(allTasks);
        } else {
            const tasksList = document.getElementById('tasks-list');
            if (tasksList) tasksList.innerHTML = '<div class="error">❌ Ошибка загрузки задач</div>';
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        const tasksList = document.getElementById('tasks-list');
        if (tasksList) tasksList.innerHTML = '<div class="error">❌ Ошибка соединения с сервером</div>';
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
        <div class="task-item" onclick="openTaskDetail(${task.id})">
            <div class="task-item-header">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-status ${task.status}">${getStatusText(task.status)}</div>
            </div>
            <div class="task-description">${escapeHtml(task.description?.substring(0, 100) || '📝 Нет описания')}${task.description?.length > 100 ? '...' : ''}</div>
            <div class="task-meta">
                <span>🎯 ${getPriorityText(task.priority)}</span>
                <span>📅 ${new Date(task.created_at).toLocaleDateString()}</span>
                ${task.due_date ? `<span>⏰ Срок: ${new Date(task.due_date).toLocaleDateString()}</span>` : ''}
            </div>
            <div class="task-actions" onclick="event.stopPropagation()">
                <select onchange="updateTaskStatus(${task.id}, this.value)" class="status-select">
                    <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>⏳ Ожидает</option>
                    <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>🔄 В работе</option>
                    <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>✅ Выполнена</option>
                </select>
                <button onclick="deleteTask(${task.id})" class="delete-btn-small">🗑</button>
            </div>
        </div>
    `).join('');
}

function filterTasks() {
    displayTasks(allTasks);
}

function openTaskDetail(taskId) {
    window.location.href = `task-detail.html?id=${taskId}`;
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({status: newStatus})
        });
        
        if (response.ok) {
            await loadTasks();
            await loadStatistics();
            showSuccessMessage('Статус обновлен');
        } else {
            showErrorMessage('Ошибка обновления статуса');
        }
    } catch (error) {
        showErrorMessage('Ошибка соединения');
    }
}

async function deleteTask(taskId) {
    if (!confirm('🗑 Удалить задачу?')) return;
    
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            await loadTasks();
            await loadStatistics();
            showSuccessMessage('Задача удалена');
        } else {
            showErrorMessage('Ошибка удаления');
        }
    } catch (error) {
        showErrorMessage('Ошибка соединения');
    }
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
    
    if (barLow) barLow.style.width = `${priorityStats.percentages.low}%`;
    if (barMedium) barMedium.style.width = `${priorityStats.percentages.medium}%`;
    if (barHigh) barHigh.style.width = `${priorityStats.percentages.high}%`;
    
    if (percentLow) percentLow.textContent = `${priorityStats.percentages.low}%`;
    if (percentMedium) percentMedium.textContent = `${priorityStats.percentages.medium}%`;
    if (percentHigh) percentHigh.textContent = `${priorityStats.percentages.high}%`;
}

async function createTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('task-title').value;
    if (!title.trim()) {
        showError('task-error', '❌ Название задачи не может быть пустым');
        return;
    }
    if (title.length > 200) {
        showError('task-error', '❌ Название не может быть длиннее 200 символов');
        return;
    }
    
    const description = document.getElementById('task-desc').value;
    const priority = parseInt(document.getElementById('task-priority').value);
    const dueDate = document.getElementById('task-due-date').value;
    
    const taskData = {
        title: title.trim(),
        description: description || null,
        priority: priority,
        status: 'pending'
    };
    
    if (dueDate) {
        taskData.due_date = new Date(dueDate).toISOString();
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            closeCreateTaskModal();
            document.getElementById('create-task-form').reset();
            await loadTasks();
            await loadStatistics();
            showSuccessMessage('Задача создана!');
        } else {
            const error = await response.json();
            showError('task-error', '❌ ' + (error.detail || 'Ошибка создания задачи'));
        }
    } catch (error) {
        showError('task-error', '❌ Ошибка соединения с сервером');
    }
}

function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'toast-success';
    successDiv.textContent = '✅ ' + message;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'toast-error';
    errorDiv.textContent = '❌ ' + message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

function showTasks() {
    const tasksSection = document.getElementById('tasks-section');
    const statsSection = document.getElementById('statistics-section');
    if (tasksSection) tasksSection.style.display = 'block';
    if (statsSection) statsSection.style.display = 'none';
    const url = new URL(window.location);
    url.searchParams.delete('tab');
    window.history.pushState({}, '', url);
}

function showStatistics() {
    const tasksSection = document.getElementById('tasks-section');
    const statsSection = document.getElementById('statistics-section');
    if (tasksSection) tasksSection.style.display = 'none';
    if (statsSection) statsSection.style.display = 'block';
    loadStatistics();
    const url = new URL(window.location);
    url.searchParams.set('tab', 'stats');
    window.history.pushState({}, '', url);
}

function showCreateTaskModal() {
    const modal = document.getElementById('create-task-modal');
    if (modal) modal.style.display = 'flex';
}

function closeCreateTaskModal() {
    const modal = document.getElementById('create-task-modal');
    if (modal) modal.style.display = 'none';
    document.getElementById('create-task-form')?.reset();
    const errorDiv = document.getElementById('task-error');
    if (errorDiv) errorDiv.style.display = 'none';
}

document.getElementById('create-task-form')?.addEventListener('submit', createTask);

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