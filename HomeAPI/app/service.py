from typing import Dict, Any, List
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status

from HomeAPI.app.const import Category
from HomeAPI.app.schema import TaskCreate

from pathlib import Path
import aiosqlite

DB_PATH = Path(__file__).parent / 'task_db.db'

def convert_to_dict(query: List) -> List[Dict[str, Any]]:
    result = []
    for tup in query:
        result.append({
            'id': tup[0],
            'title': tup[1],
            'description': tup[2],
            'done': bool(tup[3]),
            'subject': tup[4],
            'priority': tup[5],
            'category': tup[6]
        })
    return result


async def find_task(task_id: int) -> Dict[str, Any]:
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.cursor()
    await cursor.execute(f"""SELECT * FROM tasks WHERE id = {task_id};""")
    result = convert_to_dict(await cursor.fetchall())
    await db.commit()
    await db.close()
    if result != []:
        return result[0]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Не найдена задача')

async def patch_dump(task: Dict) -> None:
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.cursor()
    await cursor.execute(f"""UPDATE tasks 
    SET id = {task['id']},
    title = '{task['title']}',
    description = '{task['description']}',
    done = '{task['done']}',
    subject = '{task['subject']}',
    priority = {task['priority']},
    category = '{task['category']}'
    WHERE id = {task['id']};""")
    await db.commit()
    await db.close()


async def get_tasks_by_query(
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
        category: Category | None = None,
) -> List[Dict]:
    new_tasks = await get_all_tasks()
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


async def task_update_by_schema(task_id: int, task_update: BaseModel) -> None:
    task = await find_task(task_id=task_id)
    update_data = task_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет данных для обновления',
        )
    task.update(update_data)
    await patch_dump(task=task)


async def post_task(task: TaskCreate) -> Dict[str, Any]:
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.cursor()
    await cursor.execute("SELECT MAX(id) FROM tasks;")
    id = (await cursor.fetchone())[0] + 1
    new_task = {"id": id, **task.model_dump()}
    await cursor.execute(f"""INSERT INTO tasks
    VALUES({new_task['id']},
    '{new_task['title']}',
    '{new_task['description']}',
    '{new_task['done']}',
    '{new_task['subject']}',
     {new_task['priority']},
    '{new_task['category']}');""")
    await db.commit()
    await db.close()
    return new_task


async def delete_task_from_json(task_id: int) -> None:
    task = await find_task(task_id=task_id)
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.cursor()
    await cursor.execute(f"DELETE FROM tasks WHERE id = {task['id']};")
    await db.commit()
    await db.close()

async def get_all_tasks():
    db = await aiosqlite.connect(DB_PATH)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM tasks;")
    result = convert_to_dict(await cursor.fetchall())
    print(result)
    await db.commit()
    await db.close()
    return result