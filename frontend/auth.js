// Регистрация
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('reg-email').value;
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    // Валидация на фронте
    if (password.length < 6) {
        showError('reg-error', '❌ Пароль должен быть не менее 6 символов');
        return;
    }
    if (password.length > 72) {
        showError('reg-error', '❌ Пароль не может быть длиннее 72 символов');
        return;
    }
    
    const usernameRegex = /^[a-zA-Z0-9_]+$/;
    if (!usernameRegex.test(username)) {
        showError('reg-error', '❌ Имя пользователя может содержать только буквы, цифры и _');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, username, password})
        });
        
        if (response.ok) {
            showSuccess('reg-error', '✅ Регистрация успешна! Перенаправляем на вход...');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            const error = await response.json();
            showError('reg-error', '❌ ' + (error.detail || 'Ошибка регистрации'));
        }
    } catch (error) {
        showError('reg-error', '❌ Ошибка соединения с сервером. Убедитесь, что бэкенд запущен на http://127.0.0.1:8000');
    }
});

// Вход
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
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
            localStorage.setItem('token', data.access_token);
            window.location.href = 'dashboard.html';
        } else {
            const error = await response.json();
            showError('login-error', '❌ ' + (error.detail || 'Неверный email или пароль'));
        }
    } catch (error) {
        showError('login-error', '❌ Ошибка соединения с сервером');
    }
});