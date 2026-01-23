"""Persistence layer for tasks in the database.

Tasks come from two sources:
1. TodoWrite tool events (legacy)
2. Task file system (~/.claude/tasks/{session_id}/*.json)

Both are persisted to the database to survive file system cleanup by Claude Code.
"""

import logging

from sqlalchemy import delete, select

from app.db.database import AsyncSessionLocal
from app.db.models import TaskRecord
from app.models.common import TodoItem, TodoStatus

logger = logging.getLogger(__name__)


async def save_tasks(session_id: str, todos: list[TodoItem]) -> None:
    """Save tasks to the database, replacing any existing tasks for the session.

    Args:
        session_id: The session identifier
        todos: List of TodoItem objects to save
    """
    async with AsyncSessionLocal() as db:
        # Delete existing tasks for this session
        await db.execute(delete(TaskRecord).where(TaskRecord.session_id == session_id))

        # Insert new tasks
        for idx, todo in enumerate(todos):
            task_record = TaskRecord(
                session_id=session_id,
                task_id=str(idx + 1),  # Use 1-based index as task ID
                content=todo.content,
                status=todo.status.value,
                active_form=todo.active_form,
                sort_order=idx,
            )
            db.add(task_record)

        await db.commit()
        logger.debug(f"Saved {len(todos)} tasks for session {session_id}")


async def load_tasks(session_id: str) -> list[TodoItem]:
    """Load tasks from the database for a session.

    Args:
        session_id: The session identifier

    Returns:
        List of TodoItem objects sorted by sort_order
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TaskRecord)
            .where(TaskRecord.session_id == session_id)
            .order_by(TaskRecord.sort_order.asc())
        )
        records = result.scalars().all()

        todos: list[TodoItem] = []
        for record in records:
            try:
                status = TodoStatus(record.status)
            except ValueError:
                status = TodoStatus.PENDING

            todos.append(
                TodoItem(
                    content=record.content,
                    status=status,
                    active_form=record.active_form,
                )
            )

        logger.debug(f"Loaded {len(todos)} tasks for session {session_id}")
        return todos


async def clear_tasks(session_id: str) -> None:
    """Clear all tasks for a session.

    Args:
        session_id: The session identifier
    """
    async with AsyncSessionLocal() as db:
        await db.execute(delete(TaskRecord).where(TaskRecord.session_id == session_id))
        await db.commit()
        logger.debug(f"Cleared tasks for session {session_id}")
