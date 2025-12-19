from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


# PUBLIC_INTERFACE
class TaskCreate(BaseModel):
    """Pydantic model for creating a new task."""
    title: str = Field(..., description="Short title of the task", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Optional description/details of the task")


# PUBLIC_INTERFACE
class TaskUpdate(BaseModel):
    """Pydantic model for updating an existing task."""
    title: Optional[str] = Field(None, description="Updated title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Updated description")
    completed: Optional[bool] = Field(None, description="Updated completion status")


# PUBLIC_INTERFACE
class Task(BaseModel):
    """Serialized Task returned by the API."""
    id: int = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Short title of the task")
    description: Optional[str] = Field(None, description="Optional description/details of the task")
    completed: bool = Field(..., description="Completion status of the task")

    @staticmethod
    def from_row(row: tuple) -> "Task":
        """Helper to convert a sqlite row tuple into a Task object."""
        task_id, title, description, completed = row
        return Task(id=task_id, title=title, description=description, completed=bool(completed))
