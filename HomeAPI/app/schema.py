from pydantic import BaseModel, Field
from HomeAPI.app.const import Category

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str = Field(default='', max_length=300)
    done: bool = False
    priority: int = Field(default=3, ge=1, le=5)
    subject: str = Field(min_length=3, max_length=12)
    category: Category | None

class TaskRead(TaskCreate):
    id: int

class TaskUpdate(BaseModel):
    title: str | None = Field(min_length=3, max_length=80, default=None)
    description: str | None = Field(max_length=300, default=None)
    done: bool | None=None
    priority: int | None = Field(ge=1, le=5, default=None)
    subject: str | None = Field(min_length=3, max_length=12, default=None)
    category: Category | None=None

class DescUpdate(BaseModel):
    description: str | None = Field(max_length=300, default=None)

class TitleUpdate(BaseModel):
    title: str | None = Field(min_length=3, max_length=80, default=None)

class DoneUpdate(BaseModel):
    done: bool | None=None

class PriorityUpdate(BaseModel):
    priority: int | None = Field(ge=1, le=5, default=None)

class SubjectUpdate(BaseModel):
    subject: str | None = Field(min_length=3, max_length=12, default=None)

class CategoryUpdate(BaseModel):
    category: Category | None=None