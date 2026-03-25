import pytest

def test_task_response_schema_validation(client, auth_headers):
    """Контрактный тест: проверка схемы ответа задачи"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Contract Test Task"
    })
    assert create_response.status_code == 201
    
    task_data = create_response.json()
    # Проверяем наличие всех обязательных полей
    required_fields = ["id", "title", "description", "status", "priority", "created_at", "updated_at", "owner_id"]
    for field in required_fields:
        assert field in task_data
    
    # Проверяем типы данных
    assert isinstance(task_data["id"], int)
    assert isinstance(task_data["title"], str)
    assert isinstance(task_data["status"], str)
    assert isinstance(task_data["priority"], int)

def test_user_response_schema_validation(client, auth_headers):
    """Контрактный тест: проверка схемы ответа пользователя"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    
    user_data = response.json()
    required_fields = ["id", "email", "username", "is_active", "created_at"]
    for field in required_fields:
        assert field in user_data

def test_error_response_format(client):
    """Контрактный тест: проверка формата ошибок"""
    response = client.get("/auth/me")  # Без токена
    assert response.status_code == 401
    
    error_data = response.json()
    assert "detail" in error_data

def test_pagination_contract(client, auth_headers):
    """Контрактный тест: проверка параметров пагинации"""
    # Создаем 5 задач
    for i in range(5):
        client.post("/tasks/", headers=auth_headers, json={"title": f"Task {i}"})
    
    # Проверяем, что параметры skip и limit работают
    response = client.get("/tasks/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2