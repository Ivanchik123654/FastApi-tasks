import json
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from starlette import status

from firstAPI.schema import TaskRead, TaskCreate

app = FastAPI(
    title='HomeAPI',
    version='0.0.1',
)

with open('firstAPI\db.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)


@app.get("/", summary='Главная страница')
def read_root() -> Dict[str, str]:
    return {'message': 'Hello'}


@app.get('/health', summary='Проверить подключение')
def health_check() -> Dict[str, str]:
    return {'status': 'Ok'}


@app.get('/about', summary='эбаут')
def about() -> Dict[str, str]:
    return {
        'Project': 'ToDo',
        'Desc': 'StudyAPI',
        'Author': 'Ivan',
    }


@app.get('/student', summary='Получить информацию о ученике')
def get_student(name, age, target) -> Dict[str, str]:
    return {
        'name': name,
        'age': age,
        'target': target,
    }


@app.get(path="/tasks", summary='Получить задачи', response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_tasks(
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
) -> List[Dict]:
    new_tasks = tasks
    if done != None:
        # return list(filter(lambda x: x["done"]==done, tasks))
        new_tasks = [task for task in new_tasks if task["done"] == done]
    if title != None:
        new_tasks = [task for task in new_tasks if task["title"].lower() == title.lower()]
    if subject != None:
        new_tasks = [task for task in new_tasks if task["subject"].lower() == subject.lower()]
    print(tasks)
    return new_tasks[:limit]


@app.get("/tasks/summary", summary='Общее количество задач и сколько из них выполнено')
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


@app.get("/tasks/count-by-subject", status_code=status.HTTP_200_OK, summary='Количество задач по предмету')
def get_number_tasks(subject: str) -> Dict[str, int]:
    num_of_tasks = len([task for task in tasks if task["subject"] == subject])
    if num_of_tasks > 0:
        return {"number of tasks": num_of_tasks}
    raise HTTPException(status_code=404, detail='Subject not found')


@app.get("/tasks/by-subject/{subject}", status_code=status.HTTP_200_OK, summary='Задачи по предмету', response_model=TaskRead)
def get_task_by_subject(subject: str) -> List[Dict]:
    tasks_by_subject = [task for task in tasks if task["subject"] == subject]
    if tasks_by_subject:
        return tasks_by_subject
    raise HTTPException(status_code=404, detail='Subject not found')


@app.get("/tasks/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK, summary='Задача по id')
def get_task_by_id(task_id: int) -> Dict[str, Any]:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail='Task id not found')

@app.post(path="/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary='Создать задачу')
def create_task(task: TaskCreate) -> Dict[str, Any]:
    global tasks
    new_id = tasks[-1]['id']
    new_task = {"id": new_id + 1, **task.model_dump()}
    tasks.append(new_task)
    with open('firstAPI\db.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    return new_task