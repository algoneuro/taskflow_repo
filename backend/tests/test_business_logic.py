import pytest
from app.crud import create_task, get_tasks
from app.schemas import TaskCreate

class TestBusinessLogic:
    """Тесты бизнес-логики и расчетов"""

    def test_task_completion_calculation(self, client, auth_headers, test_user, db_session):
        """Проверка корректности расчетов: процент выполнения"""
        user_id = test_user["id"]
        
        # Создаем 5 задач: 2 completed, 3 pending
        for i in range(2):
            create_task(db_session, TaskCreate(title=f"Task {i}", status="completed"), user_id)
        for i in range(3):
            create_task(db_session, TaskCreate(title=f"Task {i+2}", status="pending"), user_id)
        
        # Получаем статистику
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем расчеты
        assert data["total"] == 5
        assert data["by_status"]["completed"] == 2
        assert data["by_status"]["pending"] == 3
        assert data["completion_rate"] == 40.0  # (2/5)*100 = 40%
    
    def test_avg_priority_calculation(self, client, auth_headers, test_user, db_session):
        """Проверка корректности расчетов: средний приоритет"""
        user_id = test_user["id"]
        
        # Создаем задачи с разными приоритетами
        create_task(db_session, TaskCreate(title="Low", priority=1), user_id)
        create_task(db_session, TaskCreate(title="Medium", priority=2), user_id)
        create_task(db_session, TaskCreate(title="High", priority=3), user_id)
        
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        data = response.json()
        
        # (1+2+3)/3 = 2.0
        assert data["avg_priority"] == 2.0
    
    def test_workload_score_calculation(self, client, auth_headers, test_user, db_session):
        """Проверка сложной бизнес-логики: workload score"""
        user_id = test_user["id"]
        
        # Формула: (pending * 3) + (in_progress * 2) + (completed * 1)
        create_task(db_session, TaskCreate(title="Pending", status="pending"), user_id)  # +3
        create_task(db_session, TaskCreate(title="In Progress", status="in_progress"), user_id)  # +2
        create_task(db_session, TaskCreate(title="Completed", status="completed"), user_id)  # +1
        
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        data = response.json()
        
        # Ожидаемый score: 3+2+1 = 6
        assert data["workload_score"] == 6
    
    def test_priority_distribution_percentages(self, client, auth_headers, test_user, db_session):
        """Проверка расчетов: проценты распределения приоритетов"""
        user_id = test_user["id"]
        
        # Создаем 4 задачи: 2 low, 1 medium, 1 high
        create_task(db_session, TaskCreate(title="Low1", priority=1), user_id)
        create_task(db_session, TaskCreate(title="Low2", priority=1), user_id)
        create_task(db_session, TaskCreate(title="Medium", priority=2), user_id)
        create_task(db_session, TaskCreate(title="High", priority=3), user_id)
        
        response = client.get("/statistics/priority-distribution", headers=auth_headers)
        data = response.json()
        
        assert data["percentages"]["low"] == 50.0  # 2/4*100
        assert data["percentages"]["medium"] == 25.0  # 1/4*100
        assert data["percentages"]["high"] == 25.0  # 1/4*100
    
    def test_edge_case_empty_tasks_calculations(self, client, auth_headers):
        """Граничный случай: пустой список задач (деление на ноль)"""
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        data = response.json()
        
        assert data["total"] == 0
        assert data["avg_priority"] == 0  # Не должно быть ошибки деления на ноль
        assert data["completion_rate"] == 0
    
    def test_edge_case_single_task_calculations(self, client, auth_headers, test_user, db_session):
        """Граничный случай: одна задача"""
        user_id = test_user["id"]
        create_task(db_session, TaskCreate(title="Only Task", priority=2, status="in_progress"), user_id)
        
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        data = response.json()
        
        assert data["total"] == 1
        assert data["avg_priority"] == 2.0
        assert data["completion_rate"] == 0.0
        assert data["by_status"]["in_progress"] == 1
    
    def test_complex_scenario_calculations(self, client, auth_headers, test_user, db_session):
        """Сложный сценарий: смешанные статусы и приоритеты"""
        user_id = test_user["id"]
        
        tasks_data = [
            (1, "pending"),      # low priority, pending
            (1, "completed"),    # low priority, completed
            (2, "pending"),      # medium priority, pending
            (3, "in_progress"),  # high priority, in_progress
            (3, "completed")     # high priority, completed
        ]
        
        for priority, status in tasks_data:
            create_task(db_session, TaskCreate(title="Task", priority=priority, status=status), user_id)
        
        response = client.get("/statistics/tasks-summary", headers=auth_headers)
        data = response.json()
        
        # Проверяем расчеты вручную
        # total = 5
        # pending = 2, in_progress = 1, completed = 2
        # avg_priority = (1+1+2+3+3)/5 = 10/5 = 2.0
        # completion_rate = (2/5)*100 = 40%
        # workload_score = (2*3)+(1*2)+(2*1) = 6+2+2 = 10
        
        assert data["total"] == 5
        assert data["by_status"]["pending"] == 2
        assert data["by_status"]["in_progress"] == 1
        assert data["by_status"]["completed"] == 2
        assert data["avg_priority"] == 2.0
        assert data["completion_rate"] == 40.0
        assert data["workload_score"] == 10