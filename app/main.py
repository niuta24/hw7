import logging

from celery.result import AsyncResult
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from celery_tasks import celery_app, check_text_for_keywords
from alert_engine import check_for_alerts
from setup_logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI()


class TaskRequest(BaseModel):
    task: str


@app.post("/process")
async def submit_task(payload: TaskRequest = Body(...)):
    if not payload.task:
        raise HTTPException(status_code=400, detail="Task cannot be empty.")

    logger.info(f"Received task: {payload.task}")
    check_for_alerts(payload.task)

    task = check_text_for_keywords.delay(payload.task)
    logger.info(f"Task {task.id} submitted to Celery")
    return JSONResponse({"task_id": task.id, "status": "ACCEPTED"})


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.state
    result = None

    if status == "SUCCESS":
        result = task_result.result
    elif status == "FAILURE":
        result = str(task_result.result)

    return JSONResponse({"task_id": task_id, "status": status, "result": result})


@app.get("/")
async def root():
    return {"message": "Hello World!"}
