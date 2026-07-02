from typing import Dict, Any, List
from fastapi import HTTPException
import json
from pydantic import BaseModel
from starlette import status

from HomeAPI.app.const import Category
from HomeAPI.app.schema import TaskCreate

with open('HomeAPI/app/db.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

def find_task(task_id:int) -> Dict[str, Any]:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail='Task id not found')

def patch_dump(task: Dict) -> None:
    for t in tasks:
        if t["id"] == task["id"]:
            tasks[tasks.index(t)] = task
            with open('HomeAPI/app/db.json', 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_tasks_by_query(
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
        category: Category | None = None,
) -> List[Dict]:
    new_tasks = tasks
    if done != None:
        # return list(filter(lambda x: x["done"]==done, tasks))
        new_tasks = [task for task in new_tasks if task["done"] == done]
    if title != None:
        new_tasks = [task for task in new_tasks if task["title"].lower() == title.lower()]
    if subject != None:
        new_tasks = [task for task in new_tasks if task["subject"].lower() == subject.lower()]
    if category != None:
        new_tasks = [task for task in new_tasks if task["category"].lower() == category.lower()]
    return new_tasks[:limit]

def task_update_by_schema(task_id: int, task_update: BaseModel) -> None:
    task = find_task(task_id=task_id)
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет данных для обновления',
            )
    task.update(update_data)
    patch_dump(task=task)

def post_task(task: TaskCreate) -> Dict[str, Any]:
    global tasks
    new_id = tasks[-1]['id']
    new_task = {"id": new_id + 1, **task.model_dump()}
    tasks.append(new_task)
    with open('HomeAPI/app/db.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    return new_task

def delete_task_from_json(task_id: int) -> None:
    task = find_task(task_id=task_id)
    tasks.remove(task)
    with open('HomeAPI/app/db.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)