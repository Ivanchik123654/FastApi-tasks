from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str = Field(default='', max_length=300)
    done: bool = False
    priority: int = Field(default=3, ge=1, le=5)
    subject: str = Field(min_length=3, max_length=12)

class TaskRead(TaskCreate):
    id: int