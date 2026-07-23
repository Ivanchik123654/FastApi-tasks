import asyncio
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status

from HomeAPI.app.schema import TaskRead, TaskCreate, TaskUpdate, DescUpdate, TitleUpdate, PriorityUpdate, SubjectUpdate, CategoryUpdate
from HomeAPI.app.const import Category
from HomeAPI.app.service import get_tasks_by_query, find_task, task_update_by_schema, patch_dump, get_all_tasks
from HomeAPI.app.service import post_task, delete_task_from_json
from HomeAPI.app.dependencies import verify_token, SessionDepends
from HomeAPI.app.external import get_hint, get_task_difficult, count_completed, count_high_priority, sort_tasks, get_motivation_by_subject

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get(path="",
            summary='Получить задачи',
            response_model=list[TaskRead],
            status_code=status.HTTP_200_OK,
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
            )
async def get_tasks(
        session: SessionDepends,
        done: bool | None = None,
        title: str | None = None,
        subject: str | None = None,
        limit: int | None = None,
        category: Category | None = None,
) -> List[Dict]:
    return await get_tasks_by_query(
        done=done,
        title=title,
        subject=subject,
        limit=limit,
        category=category,
        session=session,
    )

@router.get(
    path='/status',
    status_code=status.HTTP_200_OK,
    summary='Получить отчет по задачам',
    tags=['status'],
    dependencies=[Depends(verify_token)],
    )
async def report(session: SessionDepends) -> Dict[str, int]:
    tasks = await get_all_tasks(session=session)
    completed = asyncio.create_task(count_completed(tasks=tasks))
    high_pr = asyncio.create_task(count_high_priority(tasks=tasks))
    return {'completed': await completed, 'high_priority': await high_pr}


@router.get(path="/{task_id}",
            response_model=TaskRead,
            status_code=status.HTTP_200_OK,
            summary='Задача по id',
            tags=['tasks'],
            dependencies=[Depends(verify_token)],
            )
async def get_task_by_id(session: SessionDepends,task_id: int) -> Dict[str, Any]:
    return await find_task(task_id=task_id, session=session)


@router.post(path="",
             response_model=TaskRead,
             status_code=status.HTTP_201_CREATED,
             summary='Создать задачу',
             tags=['tasks'],
             dependencies=[Depends(verify_token)],
             )
async def create_task(session: SessionDepends, task: TaskCreate) -> Dict[str, Any]:
    return await post_task(task=task.model_dump(), session=session)


@router.patch(path="/{task_id}",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_task(session: SessionDepends,task_id: int, task_update: TaskUpdate) -> None:
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)


@router.delete(
    path="/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалять задачу',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def delete_task(session: SessionDepends, task_id: int) -> None:
    await delete_task_from_json(task_id=task_id, session=session)


@router.patch(path="/{task_id}/done",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_done(session: SessionDepends, task_id: int):
    task = await find_task(task_id=task_id, session=session)
    task["done"] = not task["done"]
    await patch_dump(task=task, session=session)

@router.patch(path="/{task_id}/description",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить описание задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_desc(session: SessionDepends, task_id: int, task_update: DescUpdate):
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)


@router.patch(path="/{task_id}/title",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_title(session: SessionDepends, task_id: int, task_update: TitleUpdate):
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)


@router.patch(path="/{task_id}/priority",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить приоритет задачу',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_priority(session: SessionDepends, task_id: int, task_update: PriorityUpdate):
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)


@router.patch(path="/{task_id}/subject",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_subject(session: SessionDepends, task_id: int, task_update: SubjectUpdate):
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)


@router.patch(path="/{task_id}/category",
              status_code=status.HTTP_204_NO_CONTENT,
              summary='Изменить название задачи',
              tags=['tasks'],
              dependencies=[Depends(verify_token)],
              )
async def update_category(session: SessionDepends, task_id: int, task_update: CategoryUpdate):
    await task_update_by_schema(task_id=task_id, task_update=task_update, session=session)

@router.get(
    path='/{task_id}/hint',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_task_hint(session: SessionDepends, task_id: int ) -> Dict[str, Any]:
    task = await find_task(task_id, session=session)
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
async def get_motivation(session: SessionDepends, task_id: int) -> Dict[str, Any]:
    tasks = await get_all_tasks(session=session)
    motivation, subject_list = await asyncio.gather(
        get_motivation_by_subject(await find_task(task_id=task_id, session=session)),
        sort_tasks(tasks=tasks, subject=await find_task(task_id=task_id, session=session)['subject'])
    )
    return {'motivation': motivation, 'sorted_subject_list_by_priority': subject_list}


@router.get(
    path='/{task_id}/motivation/2',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_motivation(session: SessionDepends, task_id: int) -> Dict[str, Any]:
    tasks = await get_all_tasks(session=session)
    motivation = await get_motivation_by_subject(await find_task(task_id=task_id, session=session))
    subject_list = await sort_tasks(tasks=tasks, subject=await find_task(task_id=task_id, session=session)['subject'])
    return {'motivation': motivation, 'sorted_subject_list_by_priority': subject_list}


@router.get(
    path='/{task_id}/motivation/3',
    status_code=status.HTTP_200_OK,
    summary='Получить подсказку по предмету',
    tags=['tasks'],
    dependencies=[Depends(verify_token)],
)
async def get_motivation(session: SessionDepends, task_id: int) -> Dict[str, Any]:
    tasks = await get_all_tasks(session=session)
    motivation = asyncio.create_task(get_motivation_by_subject(await find_task(task_id=task_id), session=session))
    subject_list = asyncio.create_task(sort_tasks(tasks=tasks, subject=await find_task(task_id=task_id, session=session)['subject']))
    return {'motivation': await motivation, 'sorted_subject_list_by_priority': await subject_list}