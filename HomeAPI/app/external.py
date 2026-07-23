import asyncio
from typing import List, Dict, Any

async def get_hint(subject: str) -> str:
    await asyncio.sleep(5)
    hints = {
        'math': '2+2=4',
        'english': 'повтори последние 5 слов',
        'home': 'пылесос в кладовке'
    }
    return hints.get(subject, 'разбей задачи на маленькие шаги')

async def get_task_difficult(priority: int) -> str:
    await asyncio.sleep(5)
    if priority < 3:
        return 'Это легко'
    elif priority < 4:
        return 'Это нормально'
    else:
        return 'Это сложно'

async def count_completed(tasks: List[Dict]) -> int:
    await asyncio.sleep(5)
    return len([task for task in tasks if task['done']])

async def count_high_priority(tasks: List[Dict]) -> int:
    await asyncio.sleep(5)
    return len([task for task in tasks if task['priority'] in [4,5]])

async def get_motivation_by_subject(task: Dict[str, Any]) -> str:
    await asyncio.sleep(5)
    if task['priority'] < 3:
        return "Маленькие дела создают большие привычки. Просто начни!"
    elif task['priority'] < 4:
        return "Сделай этот шаг — и ты будешь ближе к цели, чем кажется."
    else:
        return "Эта задача — твой главный рывок сегодня! Ты готов?"

async def sort_tasks(tasks: List[Dict], subject: str) -> List[int]:
    return sorted([task['id'] for task in tasks if task['subject'] == subject])