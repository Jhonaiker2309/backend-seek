from pydantic import BaseModel
from typing import Optional, Literal

class TaskUpdate(BaseModel):
    """Model for optional fields when updating a task."""
    title: Optional[str] = None  # Optional title field
    description: Optional[str] = None  # Optional description field
    completed: Optional[Literal["to do", "in progress", "finished"]] = None  # Optional status field

class Task(BaseModel):
    id: Optional[str] = None
    title: str  # Task title
    description: Optional[str] = None  # Task description
    completed: Literal["to do", "in progress", "finished"] = "to do"  # Task status with default value
    user_email: str  # Associated user email

    class Config:
        allow_mutation = True  # Allows changes to the fields