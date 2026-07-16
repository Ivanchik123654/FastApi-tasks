from typing import Dict, Any, List
from fastapi import HTTPException
import json
from pydantic import BaseModel
from starlette import status
import sqlite3
from pathlib import Path

from HomeAPI.app.const import Category
from HomeAPI.app.schema import TaskCreate

from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent / 'task_db.db'
db = sqlite3.connect(DB_PATH)
cursor = sqlite3.Cursor(db)

cursor.execute('SELECT * FROM tasks;')
rows = cursor.fetchall()
tasks = []
for row in rows:
    tasks.append(
        {'id': row[0],
         'title': row[1],
         'description': row[2],
         'done': row[3],
         'subject': row[4],
         'priority': row[5],
         'category': row[6]}
    )
db.commit()
db.close()

# DB_PATH = Path(__file__).parent / 'db.json'
#
# with open(DB_PATH, 'r', encoding='utf-8') as f:
#     tasks = json.load(f)

def find_task(task_id: int) -> Dict[str, Any]:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail='Task id not found')


def patch_dump(task: Dict) -> None:
    for t in tasks:
        if t['id'] == task['id']:
            tasks[tasks.index(t)] = task

    db = sqlite3.connect(DB_PATH)
    cursor = sqlite3.Cursor(db)
    cursor.execute(f"""UPDATE tasks 
    SET id = {task['id']},
    title = '{task['title']}',
    description = '{task['description']}',
    done = '{task['done']}',
    subject = '{task['subject']}',
    priority = {task['priority']},
    category = '{task['category']}'
    WHERE id = {task['id']}""")
    db.commit()
    db.close()


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
    db = sqlite3.connect(DB_PATH)
    cursor = sqlite3.Cursor(db)
    new_id = tasks[-1]['id']
    new_task = {"id": new_id + 1, **task.model_dump()}
    tasks.append(new_task)
    cursor.execute(f"""INSERT INTO tasks
    VALUES({new_task['id']},
    '{new_task['title']}',
    '{new_task['description']}',
    '{new_task['done']}',
    '{new_task['subject']}',
     {new_task['priority']},
    '{new_task['category']}')""")
    db.commit()
    db.close()
    return new_task


def delete_task_from_json(task_id: int) -> None:
    task = find_task(task_id=task_id)
    tasks.remove(task)

    db = sqlite3.connect(DB_PATH)
    cursor = sqlite3.Cursor(db)
    cursor.execute(f"DELETE FROM tasks WHERE id = {task['id']}")
    db.commit()
    db.close()