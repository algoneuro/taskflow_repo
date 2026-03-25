import pytest
from playwright.sync_api import Page, expect
import time
import os
import requests
import datetime
import uuid

BASE_URL = "http://localhost:5500"
API_URL = "http://127.0.0.1:8000"

class TestUIAuthentication:
    """UI тесты аутентификации"""

    def test_register_user_ui(self, page: Page):
        """Регистрация нового пользователя через страницу register.html"""
        unique = uuid.uuid4().hex[:8]
        email = f"uitest_{unique}@example.com"
        username = f"uitestuser_{unique}"
        password = "uitest123"

        page.goto(f"{BASE_URL}/register.html")
        page.fill("#reg-email", email)
        page.fill("#reg-username", username)
        page.fill("#reg-password", password)
        page.click("button[type='submit']")

        # Сообщение об успехе появляется в #reg-error
        success_msg = page.wait_for_selector("#reg-error", timeout=5000)
        assert "Регистрация успешна" in success_msg.text_content()

    def test_login_user_ui(self, page: Page):
        """Вход в систему и редирект на dashboard"""
        unique = uuid.uuid4().hex[:8]
        email = f"loginui_{unique}@example.com"
        username = f"loginuser_{unique}"
        password = "loginpass123"
        requests.post(f"{API_URL}/auth/register", json={
            "email": email,
            "username": username,
            "password": password
        })

        page.goto(f"{BASE_URL}/login.html")
        page.fill("#login-email", email)
        page.fill("#login-password", password)
        page.click("button[type='submit']")

        page.wait_for_url(f"{BASE_URL}/dashboard.html", timeout=5000)
        expect(page.locator("#username-display")).to_have_text(username)

    def test_login_invalid_password_ui(self, page: Page):
        """Вход с неверным паролем – должно показаться сообщение об ошибке"""
        unique = uuid.uuid4().hex[:8]
        email = f"invalid_{unique}@example.com"
        username = f"invaliduser_{unique}"
        correct_password = "correctpass"
        requests.post(f"{API_URL}/auth/register", json={
            "email": email,
            "username": username,
            "password": correct_password
        })

        page.goto(f"{BASE_URL}/login.html")
        page.fill("#login-email", email)
        page.fill("#login-password", "wrongpass")
        page.click("button[type='submit']")

        error_msg = page.wait_for_selector("#login-error", timeout=5000)
        assert "Incorrect email or password" in error_msg.text_content()

    def test_logout_ui(self, page: Page):
        """Выход из системы с дашборда"""
        unique = uuid.uuid4().hex[:8]
        email = f"logout_{unique}@example.com"
        username = f"logoutuser_{unique}"
        password = "logout123"
        requests.post(f"{API_URL}/auth/register", json={
            "email": email,
            "username": username,
            "password": password
        })
        page.goto(f"{BASE_URL}/login.html")
        page.fill("#login-email", email)
        page.fill("#login-password", password)
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard.html", timeout=5000)

        page.click(".user-menu .btn-outline")
        page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
        expect(page.locator(".auth-buttons")).to_be_visible()


class TestUITasks:
    """UI тесты управления задачами (на дашборде)"""

    def setup_user(self, page: Page, email, username, password):
        """Регистрация и вход через UI"""
        page.goto(f"{BASE_URL}/register.html")
        page.fill("#reg-email", email)
        page.fill("#reg-username", username)
        page.fill("#reg-password", password)
        page.click("button[type='submit']")
        page.wait_for_selector("#reg-error", timeout=5000)  # дождаться успешной регистрации
        page.goto(f"{BASE_URL}/login.html")
        page.fill("#login-email", email)
        page.fill("#login-password", password)
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard.html", timeout=5000)

    def test_create_task_ui(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"taskuser_{unique}@example.com"
        username = f"taskuser_{unique}"
        password = "task123"
        self.setup_user(page, email, username, password)

        page.click("button:has-text('Новая задача')")
        page.fill("#task-title", "Моя первая задача")
        page.fill("#task-desc", "Это тестовое описание")
        page.select_option("#task-priority", "2")
        page.click("#create-task-form button[type='submit']")

        page.wait_for_selector(".task-item", timeout=5000)
        expect(page.locator(".task-title").first).to_have_text("Моя первая задача")

    def test_create_task_empty_title_ui(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"emptytitle_{unique}@example.com"
        username = f"emptytitle_{unique}"
        password = "pass123"
        self.setup_user(page, email, username, password)

        page.click("button:has-text('Новая задача')")
        # Убираем атрибут required, чтобы браузер не блокировал отправку
        page.evaluate("document.getElementById('task-title').removeAttribute('required')")
        page.fill("#task-title", "")
        page.click("#create-task-form button[type='submit']")

        error_msg = page.locator("#task-error")
        expect(error_msg).to_have_text("❌ Название задачи не может быть пустым")

    def test_change_task_status_ui(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"status_{unique}@example.com"
        username = f"statususer_{unique}"
        password = "status123"
        self.setup_user(page, email, username, password)

        token = page.evaluate("localStorage.getItem('token')")
        requests.post(f"{API_URL}/tasks/", headers={"Authorization": f"Bearer {token}"},
                      json={"title": "Задача для статуса"})
        page.reload()
        page.wait_for_selector(".task-item", timeout=5000)

        status_select = page.locator(".status-select").first
        status_select.select_option("in_progress")
        page.wait_for_selector(".task-status.in_progress", timeout=5000)
        expect(page.locator(".task-status").first).to_have_text("🔄 В работе")

    def test_delete_task_ui(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"deleteui_{unique}@example.com"
        username = f"deleteuser_{unique}"
        password = "delete123"
        self.setup_user(page, email, username, password)

        token = page.evaluate("localStorage.getItem('token')")
        requests.post(f"{API_URL}/tasks/", headers={"Authorization": f"Bearer {token}"},
                      json={"title": "Задача для удаления"})
        page.reload()
        page.wait_for_selector(".task-item", timeout=5000)

        delete_btn = page.locator(".delete-btn-small").first
        page.on("dialog", lambda dialog: dialog.accept())
        delete_btn.click()
        page.wait_for_selector(".empty-state", timeout=5000)
        expect(page.locator(".empty-state")).to_have_text("📭 Нет задач. Создайте первую задачу!")


class TestUITaskDetail:
    """Тесты детальной страницы задачи"""

    def setup_user_and_task(self, page: Page, email, username, password):
        self.setup_user(page, email, username, password)
        token = page.evaluate("localStorage.getItem('token')")
        response = requests.post(f"{API_URL}/tasks/", headers={"Authorization": f"Bearer {token}"},
                                 json={"title": "Тестовая задача", "description": "Описание", "priority": 2})
        return response.json()["id"]

    def setup_user(self, page: Page, email, username, password):
        page.goto(f"{BASE_URL}/register.html")
        page.fill("#reg-email", email)
        page.fill("#reg-username", username)
        page.fill("#reg-password", password)
        page.click("button[type='submit']")
        page.wait_for_selector("#reg-error", timeout=5000)
        page.goto(f"{BASE_URL}/login.html")
        page.fill("#login-email", email)
        page.fill("#login-password", password)
        page.click("button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/dashboard.html", timeout=5000)

    def test_open_task_detail(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"detail_{unique}@example.com"
        username = f"detailuser_{unique}"
        password = "detail123"
        task_id = self.setup_user_and_task(page, email, username, password)

        page.reload()
        page.wait_for_selector(".task-item", timeout=5000)
        page.click(".task-item")
        # Ждём появления заголовка на детальной странице, вместо ожидания URL
        page.wait_for_selector("#task-title-detail", timeout=10000)
        # Проверяем, что id в URL правильный (опционально)
        assert str(task_id) in page.url

    def test_edit_task_on_detail_page(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"edit_{unique}@example.com"
        username = f"edituser_{unique}"
        password = "edit123"
        task_id = self.setup_user_and_task(page, email, username, password)

        page.reload()
        page.wait_for_selector(".task-item", timeout=5000)
        page.click(".task-item")
        page.wait_for_selector("#task-title-detail", timeout=10000)

        title_input = page.locator("#task-title-detail")
        title_input.fill("Обновлённое название")
        page.select_option("#task-status-detail", "in_progress")
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        page.fill("#task-duedate-detail", tomorrow)
        page.click("button:has-text('Сохранить изменения')")

        # Исправленная часть
        success_msg = page.locator("#task-detail-success")
        success_msg.wait_for(timeout=5000)
        expect(success_msg).to_have_text("✅ Задача успешно обновлена")

        page.goto(f"{BASE_URL}/dashboard.html")
        page.wait_for_selector(".task-item", timeout=5000)
        expect(page.locator(".task-title").first).to_have_text("Обновлённое название")
        expect(page.locator(".task-status").first).to_have_text("🔄 В работе")

    def test_delete_task_from_detail_page(self, page: Page):
        unique = uuid.uuid4().hex[:8]
        email = f"deletedetail_{unique}@example.com"
        username = f"deletedetail_{unique}"
        password = "deletedetail123"
        task_id = self.setup_user_and_task(page, email, username, password)

        page.reload()
        page.wait_for_selector(".task-item", timeout=5000)
        page.click(".task-item")
        page.wait_for_selector("#task-title-detail", timeout=10000)

        page.on("dialog", lambda dialog: dialog.accept())
        page.click(".btn-danger")
        page.wait_for_url(f"{BASE_URL}/dashboard.html", timeout=5000)
        expect(page.locator(".empty-state")).to_have_text("📭 Нет задач. Создайте первую задачу!")