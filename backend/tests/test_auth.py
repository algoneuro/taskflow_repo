import pytest
from app.auth import verify_password, get_password_hash

# ========== Модульные тесты (5 шт) ==========

def test_hash_password_returns_string():
    """Модульный тест: хеш пароля возвращает строку"""
    hashed = get_password_hash("test123")
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_hash_is_different_from_original():
    """Модульный тест: хеш не равен исходному паролю"""
    password = "secret123"
    hashed = get_password_hash(password)
    assert hashed != password

def test_verify_correct_password():
    """Модульный тест: верификация корректного пароля"""
    password = "correct123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True

def test_verify_incorrect_password():
    """Модульный тест: верификация неверного пароля"""
    password = "correct123"
    wrong_password = "wrong123"
    hashed = get_password_hash(password)
    assert verify_password(wrong_password, hashed) is False

def test_hash_is_deterministic():
    """Модульный тест: одинаковый пароль дает разный хеш (из-за соли)"""
    password = "samepassword"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    # Хеши должны быть разными из-за соли
    assert hash1 != hash2

# ========== API тесты аутентификации ==========

def test_register_user_success(client):
    """API тест: успешная регистрация"""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    """API тест: регистрация с дубликатом email"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "anotheruser",
        "password": "pass123"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.text

def test_register_duplicate_username(client, test_user):
    """API тест: регистрация с дубликатом username"""
    response = client.post("/auth/register", json={
        "email": "another@example.com",
        "username": "testuser",
        "password": "pass123"
    })
    assert response.status_code == 400
    assert "Username already taken" in response.text

def test_register_invalid_email(client):
    """API тест: регистрация с невалидным email"""
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "username": "validuser",
        "password": "pass123"
    })
    assert response.status_code == 422

def test_register_short_password(client):
    """API тест: регистрация с коротким паролем (граничное значение)"""
    response = client.post("/auth/register", json={
        "email": "short@example.com",
        "username": "shortuser",
        "password": "123"  # меньше 6 символов
    })
    assert response.status_code == 422

def test_login_success(client, test_user):
    """API тест: успешный логин"""
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password(client, test_user):
    """API тест: логин с неверным паролем"""
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.text

def test_login_nonexistent_user(client):
    """API тест: логин несуществующего пользователя"""
    response = client.post("/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "pass123"
    })
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    """API тест: получение текущего пользователя"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_access_without_token(client):
    """API тест: доступ без токена"""
    response = client.get("/auth/me")
    assert response.status_code == 401

# ========== Дополнительные тесты для покрытия ==========

def test_get_current_user_invalid_token(client):
    """Невалидный токен должен возвращать 401"""
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.text

def test_get_current_user_nonexistent_user(client, db_session):
    """Токен с email пользователя, которого нет в БД"""
    from app.auth import create_access_token
    token = create_access_token(data={"sub": "nonexistent@example.com"})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.text

def test_get_current_user_missing_sub(client):
    """Токен без поля sub"""
    from app.auth import create_access_token
    token = create_access_token(data={})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "Could not validate credentials" in response.text

def test_inactive_user(client, db_session):
    """Попытка получить данные неактивного пользователя"""
    from app.auth import create_access_token, get_password_hash
    from app.models import User
    # Создаём неактивного пользователя
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=get_password_hash("pass"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    token = create_access_token(data={"sub": "inactive@example.com"})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert "Inactive user" in response.text