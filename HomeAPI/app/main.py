from contextlib import asynccontextmanager
from typing import Dict

import fastapi
from fastapi import FastAPI, Depends

from HomeAPI.app.DB.database import create_tables
from HomeAPI.app.routers.tasks import router as tasks_router

@asynccontextmanager
async def life_spen():
    await create_tables()
    yield

app = FastAPI(
    title='FastApi-tasks',
    version='0.0.5',
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

app.include_router(router=tasks_router)