import asyncio
from asyncio import gather
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status

from HomeAPI.app.schema import TaskRead, TaskCreate, TaskUpdate, DescUpdate, TitleUpdate, PriorityUpdate, SubjectUpdate, CategoryUpdate
from HomeAPI.app.const import Category
from HomeAPI.app.service import get_tasks_by_query, tasks, find_task, task_update_by_schema, patch_dump
from HomeAPI.app.service import post_task, delete_task_from_json
from HomeAPI.app.dependencies import verify_token
from HomeAPI.app.external import get_hint, get_task_difficult, count_completed, count_high_priority, sort_tasks, get_motivation_by_subject

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get(path="",
            summary='Получить задачи',
            response_model=list[TaskRead],
            status_code=status.HTTP_200_OK,
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
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
            path="/count-by-subject",
            status_code=status.HTTP_200_OK,
            summary='Количество задач по предмету',
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
            )
def get_number_tasks(subject: str) -> Dict[str, int]:
    num_of_tasks = len([task for task in tasks if task["subject"] == subject])
    if num_of_tasks > 0:
        return {"number of tasks": num_of_tasks}
    # raise HTTPException(status_code=404, detail='Subject not found')

@router.get(
    path='/status',
    status_code=status.HTTP_200_OK,
    summary='Получить отчет по задачам',
    tags=['status'],
    dependencies=[Depends(verify_token)],
    )
async def report() -> Dict[str, int]:
    completed = asyncio.create_task(count_completed(tasks=tasks))
    high_pr = asyncio.create_task(count_high_priority(tasks=tasks))
    return {'completed': await completed, 'high_priority': await high_pr}

@router.get(
            path="/by-subject/{subject}",
            status_code=status.HTTP_200_OK,
            summary='Задачи по предмету',
            response_model=TaskRead,
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
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
            dependencies=[Depends(verify_token)],
            )
def get_task_by_id(task_id: int) -> Dict[str, Any]:
    return find_task(task_id=task_id)


@router.post(path="",
             response_model=TaskRead,
             status_code=status.HTTP_201_CREATED,
             summary='Создать задачу',
             tags=['tasks'],
             dependencies=[Depends(verify_token)],
             )
def create_task(task: TaskCreate) -> Dict[str, Any]:
    return post_task(task=task)


@router.patch(path="/{task_id}",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_task(task_id: int, task_update: TaskUpdate) -> None:
    task_update_by_schema(task_id=task_id, task_update=task_update)


@router.delete(
    path="/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалять задачу',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
def delete_task(task_id: int) -> None:
    delete_task_from_json(task_id=task_id)


@router.patch(path="/{task_id}/done",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_done(task_id: int):
    task = find_task(task_id=task_id)
    task["done"] = not task["done"]
    task.update()
    patch_dump(task=task)

@router.patch(path="/{task_id}/description",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить описание задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_desc(task_id: int, task_update: DescUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)


@router.patch(path="/{task_id}/title",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_title(task_id: int, task_update: TitleUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)


@router.patch(path="/{task_id}/priority",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить приоритет задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_priority(task_id: int, task_update: PriorityUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)


@router.patch(path="/{task_id}/subject",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_subject(task_id: int, task_update: SubjectUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)


@router.patch(path="/{task_id}/category",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
def update_category(task_id: int, task_update: CategoryUpdate):
    task_update_by_schema(task_id=task_id, task_update=task_update)

@router.get(
    path='/{task_id}/hint',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_task_hint(task_id: int ) -> Dict[str, Any]:
    task = find_task(task_id)
    hint, difficult = await asyncio.gather(
        get_hint(subject=task['subject']),
        get_task_difficult(priority=task['priority']),
    )
    return {
        'task_id': task_id,
        'title': task['title'],
        'subject': task['subject'],
        'difficult': difficult,
        'hint': hint
    }

@router.get(
    path='/{task_id}/motivation/1',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_motivation(task_id: int) -> Dict[str, Any]:
    motivation, subject_list = await asyncio.gather(
        get_motivation_by_subject(find_task(task_id=task_id)),
        sort_tasks(tasks=tasks, subject=find_task(task_id=task_id)['subject'])
    )
    return {'motivation': motivation, 'sorted_subject_list_by_priority': subject_list}


@router.get(
    path='/{task_id}/motivation/2',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_motivation(task_id: int) -> Dict[str, Any]:
    motivation,  = await get_motivation_by_subject(find_task(task_id=task_id))
    subject_list = await sort_tasks(tasks=tasks, subject=find_task(task_id=task_id)['subject'])
    return {'motivation': motivation, 'sorted_subject_list_by_priority': subject_list}


@router.get(
    path='/{task_id}/motivation/3',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_motivation(task_id: int) -> Dict[str, Any]:
    motivation = asyncio.create_task(get_motivation_by_subject(find_task(task_id=task_id)))
    subject_list = asyncio.create_task(sort_tasks(tasks=tasks)['subject'])
    return {'motivation': await motivation, 'sorted_subject_list_by_priority': await subject_list}