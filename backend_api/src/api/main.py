from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field

from src.api.db import get_db, init_db
from src.api.models import Task, TaskCreate, TaskUpdate

import sqlite3

app = FastAPI(
    title="Todo List API",
    description="A simple FastAPI backend for managing todo tasks with SQLite.",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoint"},
        {"name": "tasks", "description": "Operations on todo tasks"},
    ],
)

# Allow frontend to call backend from any origin in preview environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize database schema on app startup."""
    init_db()


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Simple health check endpoint returning a JSON status."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/tasks",
    response_model=List[Task],
    tags=["tasks"],
    summary="List Tasks",
    description="Return all tasks ordered by id descending.",
)
def list_tasks(conn: sqlite3.Connection = Depends(get_db)) -> List[Task]:
    """List all existing tasks."""
    cur = conn.execute(
        "SELECT id, title, description, completed FROM tasks ORDER BY id DESC"
    )
    rows = cur.fetchall()
    return [Task.from_row(r) for r in rows]


# PUBLIC_INTERFACE
@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
    summary="Create Task",
    description="Create a new task with title and optional description.",
)
def create_task(payload: TaskCreate, conn: sqlite3.Connection = Depends(get_db)) -> Task:
    """Create and return the newly created task."""
    cur = conn.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, 0)",
        (payload.title, payload.description),
    )
    conn.commit()
    task_id = cur.lastrowid
    # fetch to return canonical representation
    cur = conn.execute(
        "SELECT id, title, description, completed FROM tasks WHERE id = ?", (task_id,)
    )
    row = cur.fetchone()
    return Task.from_row(row)


# PUBLIC_INTERFACE
@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["tasks"],
    summary="Update Task",
    description="Update title, description and/or completed status of a task.",
)
def update_task(task_id: int, payload: TaskUpdate, conn: sqlite3.Connection = Depends(get_db)) -> Task:
    """Update a task by id."""
    # Ensure exists
    cur = conn.execute("SELECT id, title, description, completed FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    existing = Task.from_row(row)
    new_title = payload.title if payload.title is not None else existing.title
    new_description = payload.description if payload.description is not None else existing.description
    new_completed = int(payload.completed if payload.completed is not None else existing.completed)

    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, completed = ? WHERE id = ?",
        (new_title, new_description, new_completed, task_id),
    )
    conn.commit()

    cur = conn.execute("SELECT id, title, description, completed FROM tasks WHERE id = ?", (task_id,))
    updated = cur.fetchone()
    return Task.from_row(updated)


# PUBLIC_INTERFACE
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["tasks"],
    summary="Delete Task",
    description="Delete a task by its identifier.",
)
def delete_task(task_id: int, conn: sqlite3.Connection = Depends(get_db)) -> None:
    """Delete a task. Returns 204 on success; 404 if not found."""
    cur = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return None
