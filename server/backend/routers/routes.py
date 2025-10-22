# server/backend/routers/routes.py

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.database.db import get_db, engine  # central engine + session dependency
from server.database import db_models as models

# Create tables on startup (safe in dev; for prod use Alembic migrations)
models.Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["tasks"])

# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: int
    name: str
    topic: str
    description: str

    class Config:
        from_attributes = True  # Pydantic v2 ORM mode


class MultilineData(BaseModel):
    lines: List[str]


class ChatPayload(BaseModel):
    # keep it flexible; you can tighten later to your exact chat format
    messages: List[Dict[str, Any]] | None = None
    content: str | None = None


# ──────────────────────────────────────────────────────────────────────────────
# Task endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get("/tasks", response_model=List[TaskOut])
def list_tasks(db: Session = Depends(get_db)) -> List[models.Task]:
    """Return all tasks (id, name, topic, description)."""
    return db.query(models.Task).all()


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)) -> models.Task:
    """Return one task by id or 404."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/topic/{topic}", response_model=List[TaskOut])
def get_tasks_by_topic(topic: str, db: Session = Depends(get_db)) -> List[models.Task]:
    """Return tasks filtered by topic."""
    return db.query(models.Task).filter(models.Task.topic == topic).all()


# ──────────────────────────────────────────────────────────────────────────────
# Code execution / quality checks
# (Uncomment real tool imports when those modules are in place)
# ──────────────────────────────────────────────────────────────────────────────

# from server.agentic.tools import ScriptRunner, CodeChecker
# from server.agentic.main import Assistant_agent

@router.post("/tasks/{task_id}/run")
def run_code_by_task_id(task_id: int, payload: MultilineData, db: Session = Depends(get_db)):
    """Execute user code for a given task (dev stub; wire to ScriptRunner)."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    code = "\n".join(payload.lines)
    # result = ScriptRunner.run_python_code(code)
    result = {"echo": code}  # stub so the API runs even if agentic tools aren’t ready
    return {"result": result}


@router.post("/tasks/{task_id}/manual_quality_checker")
def manual_quality_checker(task_id: int, payload: MultilineData, db: Session = Depends(get_db)):
    """Static analysis of code (dev stub; wire to CodeChecker)."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    code = "\n".join(payload.lines)
    # report = CodeChecker.check_code_with_pylint(code)
    report = {"pylint": "stubbed report"}  # stub
    return {"result": report}


@router.post("/tasks/{task_id}/ai_checker")
def ai_checker(task_id: int, payload: MultilineData, db: Session = Depends(get_db)):
    """LLM-based code review against the task’s spec and reference solution (dev stub)."""
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    code = "\n".join(payload.lines)
    problem = f"{task.name}\n{task.description}"

    # pylint_report = CodeChecker.check_code_with_pylint(code)
    # agent = Assistant_agent()
    # response = agent.run(problem, pylint_report, task.correct_code, code)
    response = {
        "problem": problem,
        "reference_present": bool(task.correct_code),
        "analysis": "stubbed ai response",
    }
    return {"result": response}


# ──────────────────────────────────────────────────────────────────────────────
# Chat endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.post("/chat")
def chat(payload: ChatPayload):
    """Generic chat endpoint (dev stub; wire to Assistant_agent)."""
    # agent = Assistant_agent()
    # return agent.invoke_llm_for_chat(payload.model_dump())
    return {
        "echo": payload.model_dump(),
        "note": "wire to Assistant_agent.invoke_llm_for_chat when ready",
    }
