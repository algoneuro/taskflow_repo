from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
from .. import auth, database, models

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/tasks-summary")
def get_tasks_summary(
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
) -> Dict:
    """Возвращает статистику по задачам пользователя с расчетами"""
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    
    total = len(tasks)
    
    # Расчеты: количество по статусам
    pending = sum(1 for t in tasks if t.status == "pending")
    in_progress = sum(1 for t in tasks if t.status == "in_progress")
    completed = sum(1 for t in tasks if t.status == "completed")
    
    # Расчеты: средний приоритет
    avg_priority = sum(t.priority for t in tasks) / total if total > 0 else 0
    
    # Расчеты: процент выполнения
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # Расчеты: weighted priority score (сложная бизнес-логика)
    # Формула: (pending * 3) + (in_progress * 2) + (completed * 1)
    workload_score = (pending * 3) + (in_progress * 2) + (completed * 1)
    
    return {
        "total": total,
        "by_status": {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        },
        "avg_priority": round(avg_priority, 2),
        "completion_rate": round(completion_rate, 2),
        "workload_score": workload_score
    }

@router.get("/priority-distribution")
def get_priority_distribution(
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
) -> Dict:
    """Возвращает распределение задач по приоритетам с процентами"""
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    total = len(tasks)
    
    low = sum(1 for t in tasks if t.priority == 1)
    medium = sum(1 for t in tasks if t.priority == 2)
    high = sum(1 for t in tasks if t.priority == 3)
    
    return {
        "distribution": {
            "low": low,
            "medium": medium,
            "high": high
        },
        "percentages": {
            "low": round(low / total * 100, 2) if total > 0 else 0,
            "medium": round(medium / total * 100, 2) if total > 0 else 0,
            "high": round(high / total * 100, 2) if total > 0 else 0
        }
    }