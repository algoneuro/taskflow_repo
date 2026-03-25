from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, crud, auth, database

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@router.get("/", response_model=List[schemas.TaskResponse])
def read_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
):
    tasks = crud.get_tasks(db, user_id=current_user.id, skip=skip, limit=limit)
    
    if status:
        tasks = [task for task in tasks if task.status == status]
    
    return tasks

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
):
    task = crud.get_task_by_id(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
):
    task = crud.update_task(db, task_id=task_id, task_update=task_update, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    current_user = Depends(auth.get_current_active_user)
):
    success = crud.delete_task(db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None