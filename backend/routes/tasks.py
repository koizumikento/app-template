from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from schemas import TaskCreateRequest, TaskResponse
from services import get_task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=202)
async def enqueue_task(
    request: TaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    task_service=Depends(get_task_service),
) -> TaskResponse:
    record = await task_service.enqueue_simple_task(session, request.model_dump())
    return TaskResponse.from_record(record)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_session),
    task_service=Depends(get_task_service),
) -> TaskResponse:
    record = await task_service.get_task(session, task_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.from_record(record)
