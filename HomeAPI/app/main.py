from typing import Dict
from fastapi import FastAPI, Depends

from HomeAPI.app.dependencies import verify_token
from HomeAPI.app.routers.tasks import router as tasks_router
from HomeAPI.app.service import tasks

app = FastAPI(
    title='HomeAPI',
    version='0.0.1',
)

@app.get(path="/", summary='Главная страница')
def read_root() -> Dict[str, str]:
    return {'message': 'Hello'}


@app.get(path='/health', summary='Проверить подключение')
def health_check() -> Dict[str, str]:
    return {'status': 'Ok'}


@app.get(path='/about', summary='эбаут')
def about() -> Dict[str, str]:
    return {
        'Project': 'ToDo',
        'Desc': 'StudyAPI',
        'Author': 'Ivan',
    }

@app.get(path='/student',
         summary='Получить информацию о ученике',
         tags=['student'],
)
def get_student(name, age, target) -> Dict[str, str]:
    return {
        'name': name,
        'age': age,
        'target': target,
    }

@app.get(
            path="/summary",
            summary='Общее количество задач и сколько из них выполнено',
            tags=['stats'],
            dependencies=[Depends(verify_token)],
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

app.include_router(router=tasks_router)