from typing import Dict

from fastapi import APIRouter, Depends
from HomeAPI.app.routers.tasks import router as tasks_router
from HomeAPI.app.dependencies import verify_token
from HomeAPI.app.service import get_all_tasks

router = APIRouter(prefix="/stats", tags=["stats"])
tasks = get_all_tasks()

@router.get(
            path="/tasks/summary",
            summary='Общее количество задач и сколько из них выполнено',
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
            )
def get_tasks_summary() -> Dict[str, int]:
    # Считаем общее количество задач и сколько из них выполнено.
    tasks = get_all_tasks()
    total = len(tasks)
    completed = len([task for task in tasks if task["done"]])
    not_completed = total - completed
    return {
        "total": total,
        "completed": completed,
        "not_completed": not_completed,
    }