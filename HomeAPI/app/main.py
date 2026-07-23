from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI

from HomeAPI.app.DB.database import create_tables
from HomeAPI.app.routers.tasks import router as tasks_router
from pathlib import Path
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def life_spen():
    await create_tables()
    yield

app = FastAPI(
    title='FastApi-tasks',
    version='0.0.5',
)

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
    path='/ui',
    response_class=HTMLResponse,
    tags=['frontend'],
)
def show_front() -> str:
    return (BASE_DIR/'static'/'index.html').read_text(encoding='utf-8')

app.include_router(router=tasks_router)