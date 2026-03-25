import pytest

def test_full_user_workflow(client):
    """Интеграционный тест: полный сценарий пользователя"""
    # 1. Регистрация
    register_response = client.post("/auth/register", json={
        "email": "workflow@example.com",
        "username": "workflowuser",
        "password": "workflow123"
    })
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]
    
    # 2. Логин
    login_response = client.post("/auth/login", data={
        "username": "workflow@example.com",
        "password": "workflow123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Создание нескольких задач
    tasks = []
    for i in range(3):
        response = client.post("/tasks/", headers=headers, json={
            "title": f"Workflow Task {i}",
            "priority": i + 1
        })
        assert response.status_code == 201
        tasks.append(response.json())
    
    # 4. Получение списка задач
    list_response = client.get("/tasks/", headers=headers)
    assert len(list_response.json()) == 3
    
    # 5. Обновление задачи
    update_response = client.put(f"/tasks/{tasks[0]['id']}", headers=headers, json={
        "status": "completed"
    })
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"
    
    # 6. Фильтрация по статусу
    filtered_response = client.get("/tasks/?status=completed", headers=headers)
    assert len(filtered_response.json()) == 1
    assert filtered_response.json()[0]["id"] == tasks[0]["id"]
    
    # 7. Удаление задачи
    delete_response = client.delete(f"/tasks/{tasks[1]['id']}", headers=headers)
    assert delete_response.status_code == 204
    
    # 8. Проверка финального состояния
    final_response = client.get("/tasks/", headers=headers)
    assert len(final_response.json()) == 2

def test_concurrent_users(client):
    """Интеграционный тест: работа нескольких пользователей одновременно"""
    users_data = [
        {"email": "user_a@example.com", "username": "usera", "password": "pass123"},
        {"email": "user_b@example.com", "username": "userb", "password": "pass123"},
        {"email": "user_c@example.com", "username": "userc", "password": "pass123"},
    ]
    
    users = []
    for user_data in users_data:
        client.post("/auth/register", json=user_data)
        login_response = client.post("/auth/login", data={
            "username": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        users.append({
            "data": user_data,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        })
    
    # Каждый пользователь создает задачи
    for user in users:
        for i in range(2):
            response = client.post("/tasks/", headers=user["headers"], json={
                "title": f"Task {i} for {user['data']['username']}"
            })
            assert response.status_code == 201
    
    # Проверяем изоляцию
    for user in users:
        response = client.get("/tasks/", headers=user["headers"])
        assert len(response.json()) == 2