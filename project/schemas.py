from typing import List, Optional, Any
from pydantic import BaseModel, Field, EmailStr


class ActionResponse(BaseModel):
    status: str
    message: Any


class UserLogIn(BaseModel):
    username: str
    password: str


class Task(BaseModel):
    id: int
    email: str
    username: str
    text: str
    status: int

    class Config:
        orm_mode = True


class TaskEdit(BaseModel):
    text: str
    status: int


class TaskCreate(BaseModel):
    email: EmailStr
    username: str
    text: str


class TaskList(BaseModel):
    tasks: List[Task]
    total_task_count: int

