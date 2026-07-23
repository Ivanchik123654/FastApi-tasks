from typing import Dict, Any, List
from unicodedata import category

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from HomeAPI.app.const import Category
from HomeAPI.app.dependencies import SessionDepends
from HomeAPI.app.models import Task
from HomeAPI.app.schema import TaskCreate
from pathlib import Path
import aiosqlite

DB_PATH = Path(__file__).parent / 'task_db.db'
SQLALCHEMY_DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

def convert_to_dict(query: List) -> List[Dict[str, Any]]:
    result = []
    for tup in query:
        done_value = tup.done.lower() == 'true'
        result.append({
            'id': tup.id,
            'title': tup.title,
            'description': tup.description,
            'done': done_value,
            'subject': tup.subject,
            'priority': tup.priority,
            'category': tup.category
        })
    return result


async def find_task(session: SessionDepends, task_id: int) -> Dict[str, Any]:
    result = convert_to_dict((await session.scalars(select(Task).where(Task.id == task_id))).all())
    await session.commit()
    if result != []:
        return result[0]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Не найдена задача')

async def patch_dump(session: SessionDepends, task: Dict) -> None:
    print(task)
    await session.execute(update(Task).where(Task.id == task['id']).values(
        title=task['title'],
        description=task['description'],
        done=str(task['done']),
        subject=task['subject'],
        priority=task['priority'],
        category=task['category'],
    ))
    await session.commit()


async def get_tasks_by_query(
        session: SessionDepends,
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
        category: Category | None = None,
) -> List[Dict]:
    new_tasks = await get_all_tasks(session=session)
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


async def task_update_by_schema(session: SessionDepends, task_id: int, task_update: BaseModel) -> None:
    task = await find_task(task_id=task_id, session=session)
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет данных для обновления',
        )
    task.update(update_data)
    await patch_dump(task=task, session=session)


async def post_task(session: SessionDepends, task: TaskCreate) -> Dict[str, Any]:
    new_task = Task(id=(await session.execute(select(func.max(Task.id)))).scalar() + 1, **task)
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return {
        'id': new_task.id,
        'title': new_task.title,
        'description': new_task.description,
        'done': new_task.done,
        'subject': new_task.subject,
        'priority': new_task.priority,
        'category': new_task.category,
    }

async def delete_task_from_json(session: SessionDepends, task_id: int) -> None:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
async def get_all_tasks(session: SessionDepends,):
    result = convert_to_dict((await session.scalars(select(Task))).all())
    return result