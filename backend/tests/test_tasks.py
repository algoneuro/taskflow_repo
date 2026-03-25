import pytest
from datetime import datetime, timedelta, timezone 

def test_create_task_success(client, auth_headers):
    """API тест: успешное создание задачи"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Test Task",
        "description": "This is a test task",
        "priority": 2
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["priority"] == 2
    assert data["status"] == "pending"
    assert "id" in data

def test_create_task_minimal_title(client, auth_headers):
    """Граничное значение: минимальная длина title (1 символ)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "A"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "A"

def test_create_task_max_title(client, auth_headers):
    """Граничное значение: максимальная длина title (200 символов)"""
    long_title = "A" * 200
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": long_title
    })
    assert response.status_code == 201
    assert len(response.json()["title"]) == 200

def test_create_task_title_too_long(client, auth_headers):
    """Негативный тест: заголовок длиннее максимального (граничное значение)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "A" * 201
    })
    assert response.status_code == 422

def test_create_task_without_title(client, auth_headers):
    """Негативный тест: создание задачи без заголовка"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "description": "Task without title"
    })
    assert response.status_code == 422
    assert "title" in response.text

def test_create_task_min_priority(client, auth_headers):
    """Граничное значение: минимальный приоритет (1)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Low Priority",
        "priority": 1
    })
    assert response.status_code == 201
    assert response.json()["priority"] == 1

def test_create_task_max_priority(client, auth_headers):
    """Граничное значение: максимальный приоритет (3)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "High Priority",
        "priority": 3
    })
    assert response.status_code == 201
    assert response.json()["priority"] == 3

def test_create_task_invalid_priority(client, auth_headers):
    """Негативный тест: приоритет выше максимального (граничное значение)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task",
        "priority": 4
    })
    assert response.status_code == 422

def test_create_task_priority_below_min(client, auth_headers):
    """Негативный тест: приоритет ниже минимального (граничное значение)"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task",
        "priority": 0
    })
    assert response.status_code == 422

def test_get_tasks_empty(client, auth_headers):
    """API тест: получение пустого списка задач"""
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_pagination(client, auth_headers):
    """API тест: пагинация задач"""
    for i in range(5):
        client.post("/tasks/", headers=auth_headers, json={"title": f"Task {i}"})
    
    response = client.get("/tasks/?skip=0&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_get_task_by_id(client, auth_headers):
    """API тест: получение задачи по ID"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Specific Task"
    })
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"

def test_get_nonexistent_task(client, auth_headers):
    """Негативный тест: получение несуществующей задачи"""
    response = client.get("/tasks/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "Task not found" in response.text

def test_update_task_success(client, auth_headers):
    """API тест: успешное обновление задачи"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Original Title",
        "status": "pending"
    })
    task_id = create_response.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
        "title": "Updated Title",
        "status": "completed"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["status"] == "completed"

def test_update_task_partial(client, auth_headers):
    """API тест: частичное обновление задачи"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task",
        "description": "Original description"
    })
    task_id = create_response.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
        "title": "Only Title Updated"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Only Title Updated"
    assert response.json()["description"] == "Original description"

def test_update_task_invalid_status(client, auth_headers):
    """Негативный тест: обновление с невалидным статусом"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task"
    })
    task_id = create_response.json()["id"]
    
    response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
        "status": "invalid_status"
    })
    assert response.status_code == 422

def test_delete_task_success(client, auth_headers):
    """API тест: успешное удаление задачи"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task to Delete"
    })
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_task_isolation(client, auth_headers):
    """Интеграционный тест: изоляция задач между пользователями"""
    # Создаем задачу первым пользователем
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "User1 Task"
    })
    task_id = create_response.json()["id"]
    
    # Создаем второго пользователя
    client.post("/auth/register", json={
        "email": "user2@example.com",
        "username": "user2",
        "password": "pass123"
    })
    login_response = client.post("/auth/login", data={
        "username": "user2@example.com",
        "password": "pass123"
    })
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # Пытаемся получить задачу первого пользователя
    response = client.get(f"/tasks/{task_id}", headers=user2_headers)
    assert response.status_code == 404
    
    # Список задач второго пользователя должен быть пуст
    tasks_response = client.get("/tasks/", headers=user2_headers)
    assert len(tasks_response.json()) == 0

# ========== Тесты due_date ==========

def test_create_task_with_due_date(client, auth_headers):
    """Создание задачи с указанием срока выполнения"""
    from datetime import datetime, timedelta
    due_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task with due date",
        "due_date": due_date
    })
    assert response.status_code == 201
    data = response.json()
    assert "due_date" in data
    assert data["due_date"] is not None
    # Проверяем, что дата сохранилась (сравниваем только дату, без миллисекунд)
    assert data["due_date"].startswith(due_date[:19])

def test_update_task_due_date(client, auth_headers):
    """Обновление срока выполнения задачи"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task to update due date"
    })
    task_id = create_response.json()["id"]

    from datetime import datetime, timedelta
    new_due_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
        "due_date": new_due_date
    })
    assert response.status_code == 200
    data = response.json()
    assert data["due_date"].startswith(new_due_date[:19])

def test_create_task_invalid_due_date_format(client, auth_headers):
    """Невалидный формат due_date должен возвращать ошибку"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task",
        "due_date": "not-a-date"
    })
    assert response.status_code == 422  # Pydantic validation error


# ========== Тесты статуса "in_progress" ==========

def test_create_task_with_in_progress_status(client, auth_headers):
    """Создание задачи со статусом 'in_progress'"""
    response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task in progress",
        "status": "in_progress"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"

def test_update_task_to_in_progress(client, auth_headers):
    """Обновление статуса задачи на 'in_progress'"""
    create_response = client.post("/tasks/", headers=auth_headers, json={
        "title": "Task to set in progress"
    })
    task_id = create_response.json()["id"]

    response = client.put(f"/tasks/{task_id}", headers=auth_headers, json={
        "status": "in_progress"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"

def test_filter_tasks_by_in_progress_status(client, auth_headers):
    """Фильтрация задач по статусу 'in_progress'"""
    # Создаём задачу со статусом in_progress
    client.post("/tasks/", headers=auth_headers, json={
        "title": "In progress task",
        "status": "in_progress"
    })
    # Создаём задачу со статусом pending
    client.post("/tasks/", headers=auth_headers, json={
        "title": "Pending task"
    })

    response = client.get("/tasks/?status=in_progress", headers=auth_headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "in_progress"

# ========== Дополнительные тесты для покрытия ==========

def test_filter_tasks_invalid_status(client, auth_headers):
    """Фильтрация по невалидному статусу должна возвращать пустой список"""
    response = client.get("/tasks/?status=invalid_status", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_update_nonexistent_task(client, auth_headers):
    """Обновление несуществующей задачи → 404"""
    response = client.put("/tasks/99999", headers=auth_headers, json={"title": "New Title"})
    assert response.status_code == 404
    assert "Task not found" in response.text

def test_delete_nonexistent_task(client, auth_headers):
    """Удаление несуществующей задачи → 404"""
    response = client.delete("/tasks/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "Task not found" in response.text