let currentTaskId = null;

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    currentToken = token;
    
    // Получаем ID задачи из URL
    const urlParams = new URLSearchParams(window.location.search);
    currentTaskId = urlParams.get('id');
    
    if (!currentTaskId) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    await loadUser();
    await loadTaskDetails();
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

async function loadTaskDetails() {
    try {
        const response = await fetch(`${API_URL}/tasks/${currentTaskId}`, {
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            const task = await response.json();
            displayTaskDetails(task);
        } else if (response.status === 404) {
            showError('task-detail-error', 'Задача не найдена');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 2000);
        } else {
            showError('task-detail-error', 'Ошибка загрузки задачи');
        }
    } catch (error) {
        showError('task-detail-error', 'Ошибка соединения с сервером');
    }
}

function displayTaskDetails(task) {
    // Заголовок
    const titleInput = document.getElementById('task-title-detail');
    if (titleInput) titleInput.value = task.title;
    
    // Описание
    const descTextarea = document.getElementById('task-description-detail');
    if (descTextarea) descTextarea.value = task.description || '';
    
    // Приоритет
    const prioritySelect = document.getElementById('task-priority-detail');
    if (prioritySelect) prioritySelect.value = task.priority;
    
    // Статус
    const statusSelect = document.getElementById('task-status-detail');
    if (statusSelect) statusSelect.value = task.status;
    
    // Статус бейдж
    const statusBadge = document.getElementById('task-status-badge');
    if (statusBadge) {
        const statusText = getStatusText(task.status);
        statusBadge.textContent = statusText;
        statusBadge.className = `task-status-badge ${task.status}`;
    }
    
    // Срок выполнения
    const dueDateInput = document.getElementById('task-duedate-detail');
    if (dueDateInput && task.due_date) {
        // Форматируем дату для input datetime-local
        const date = new Date(task.due_date);
        const formattedDate = date.toISOString().slice(0, 16);
        dueDateInput.value = formattedDate;
    } else if (dueDateInput) {
        dueDateInput.value = '';
    }
    
    // Дата создания
    const createdInput = document.getElementById('task-created-detail');
    if (createdInput && task.created_at) {
        createdInput.value = new Date(task.created_at).toLocaleString('ru-RU');
    }
    
    // Дата обновления
    const updatedInput = document.getElementById('task-updated-detail');
    if (updatedInput && task.updated_at) {
        updatedInput.value = new Date(task.updated_at).toLocaleString('ru-RU');
    }
}

async function saveTaskChanges() {
    const title = document.getElementById('task-title-detail').value;
    const description = document.getElementById('task-description-detail').value;
    const priority = parseInt(document.getElementById('task-priority-detail').value);
    const status = document.getElementById('task-status-detail').value;
    const dueDateRaw = document.getElementById('task-duedate-detail').value;
    
    // Валидация
    if (!title || title.trim() === '') {
        showError('task-detail-error', '❌ Название задачи не может быть пустым');
        return;
    }
    if (title.length > 200) {
        showError('task-detail-error', '❌ Название не может быть длиннее 200 символов');
        return;
    }
    
    const updateData = {
        title: title.trim(),
        description: description || null,
        priority: priority,
        status: status
    };
    
    if (dueDateRaw) {
        updateData.due_date = new Date(dueDateRaw).toISOString();
    } else {
        updateData.due_date = null;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${currentTaskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(updateData)
        });
        
        if (response.ok) {
            showSuccess('task-detail-success', '✅ Задача успешно обновлена');
            // Обновляем отображение статуса
            const statusBadge = document.getElementById('task-status-badge');
            if (statusBadge) {
                statusBadge.textContent = getStatusText(status);
                statusBadge.className = `task-status-badge ${status}`;
            }
            // Обновляем дату обновления
            const updatedInput = document.getElementById('task-updated-detail');
            if (updatedInput) {
                updatedInput.value = new Date().toLocaleString('ru-RU');
            }
            setTimeout(() => {
                document.getElementById('task-detail-success').style.display = 'none';
            }, 3000);
        } else {
            const error = await response.json();
            showError('task-detail-error', '❌ ' + (error.detail || 'Ошибка обновления'));
        }
    } catch (error) {
        showError('task-detail-error', '❌ Ошибка соединения с сервером');
    }
}

async function deleteCurrentTask() {
    if (!confirm('🗑 Вы уверены, что хотите удалить эту задачу?')) return;
    
    try {
        const response = await fetch(`${API_URL}/tasks/${currentTaskId}`, {
            method: 'DELETE',
            headers: {'Authorization': `Bearer ${currentToken}`}
        });
        
        if (response.ok) {
            showSuccess('task-detail-success', '✅ Задача удалена');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showError('task-detail-error', '❌ Ошибка удаления задачи');
        }
    } catch (error) {
        showError('task-detail-error', '❌ Ошибка соединения с сервером');
    }
}

function showStatistics() {
    window.location.href = 'dashboard.html?tab=stats';
}

function getStatusText(status) {
    const statuses = {
        'pending': '⏳ Ожидает',
        'in_progress': '🔄 В работе',
        'completed': '✅ Выполнена'
    };
    return statuses[status] || status;
}