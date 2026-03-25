# backend/tests/test_database.py

from app.database import get_db

def test_get_db_returns_generator():
    """Проверяем, что get_db возвращает генератор"""
    gen = get_db()
    db = next(gen)
    assert db is not None
    try:
        next(gen)  # выход из контекста
    except StopIteration:
        pass
    # Проверяем, что сессия закрыта (вызовет ошибку)
    import pytest
    with pytest.raises(Exception):
        db.execute("SELECT 1")