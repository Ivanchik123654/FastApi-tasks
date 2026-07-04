from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from starlette import status

from HomeAPI.app.schema import TaskRead, TaskCreate, TaskUpdate, DescUpdate, TitleUpdate,PriorityUpdate, SubjectUpdate, CategoryUpdate
from HomeAPI.app.const import Category
from HomeAPI.app.service import get_tasks_by_query, tasks, find_task, task_update_by_schema, patch_dump
from HomeAPI.app.service import post_task, delete_task_from_json

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get(path="",
         summary='Получить задачи',
         response_model=list[TaskRead],
         status_code=status.HTTP_200_OK,
         tags=['tasks'],
)
def get_tasks(
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
        category: Category | None = None,
) -> List[Dict]:
    return get_tasks_by_query(
        done=done,
        title=title,
        subject=subject,
        limit=limit,
        category=category
    )

@router.get(
    path="/summary",
    summary='Общее количество задач и сколько из них выполнено',
    tags=['tasks'],
)
def get_tasks_summary() -> Dict[str, int]:
    # Считаем общее количество задач и сколько из них выполнено.
    total = len(tasks)
    completed = len([task for task in tasks if task["done"]])
    not_completed = total - completed
    return {
        "total": total,
        "completed": completed,
        "not_completed": not_completed,
    }

@router.get(
    path="/count-by-subject",
    status_code=status.HTTP_200_OK,
    summary='Количество задач по предмету',
    tags=['tasks'],
)
def get_number_tasks(subject: str) -> Dict[str, int]:
    num_of_tasks = len([task for task in tasks if task["subject"] == subject])
    if num_of_tasks > 0:
        return {"number of tasks": num_of_tasks}
    #raise HTTPException(status_code=404, detail='Subject not found')

@router.get(
    path="/by-subject/{subject}",
    status_code=status.HTTP_200_OK,
    summary='Задачи по предмету',
    response_model=TaskRead,
    tags=['tasks'],
)
def get_task_by_subject(subject: str) -> List[Dict]:
    tasks_by_subject = [task for task in tasks if task["subject"] == subject]
    if tasks_by_subject:
        return tasks_by_subject
    raise HTTPException(status_code=404, detail='Subject not found')

@router.get(path="/{task_id}",
         response_model=TaskRead,
         status_code=status.HTTP_200_OK,
         summary='Задача по id',
         tags=['tasks'],
)
def get_task_by_id(task_id: int) -> Dict[str, Any]:
    return find_task(task_id=task_id)

@router.post(path="",
          response_model=TaskRead,
          status_code=status.HTTP_201_CREATED,
          summary='Создать задачу',
          tags=['tasks'],
)
def create_task(task: TaskCreate) -> Dict[str, Any]:
    return post_task(task=task)

@router.patch(path="/{task_id}",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить задачу',
           tags=['tasks']
)
def update_task(task_id: int, task_update: TaskUpdate) -> None:
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.delete(path="/{tasks_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary='Удалять задачу',
            tags=['tasks']
)
def delete_task(task_id: int) -> None:
    delete_task_from_json(task_id=task_id)

@router.patch(path="/{task_id}/done",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить задачу',
           tags=['tasks']
           )
def update_done(task_id: int):
    task = find_task(task_id=task_id)
    task["done"] = not task["done"]
    task.update()
    patch_dump(task=task)

@router.patch(path="/{task_id}/description",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить описание задачи',
           tags=['tasks']
)
def update_desc(task_id: int, task_update: DescUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.patch(path="/{task_id}/title",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить название задачу',
           tags=['tasks']
           )
def update_title(task_id: int, task_update: TitleUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.patch(path="/{task_id}/priority",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить приоритет задачу',
           tags=['tasks']
           )
def update_priority(task_id: int, task_update: PriorityUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.patch(path="/{task_id}/subject",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить название задачи',
           tags=['tasks']
           )
def update_subject(task_id: int, task_update: SubjectUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.patch(path="/{task_id}/category",
           status_code=status.HTTP_204_NO_CONTENT,
           summary='Изменить название задачи',
           tags=['tasks']
           )
def update_category(task_id: int, task_update: CategoryUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)