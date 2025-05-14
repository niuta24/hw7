import logging
import os
import time

from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

logger = logging.getLogger(__name__)


# --- Celery Task ---
@celery_app.task(bind=True, name="check_text_for_keywords")
def check_text_for_keywords(self, task_data: str):
    self.update_state(state="IN_PROGRESS")
    logger.info(f"Celery Task {self.request.id} started with input: {task_data}")

    # Simulated processing delay
    time.sleep(10)

    # Keyword detection logic
    keyword = "urgent"
    if keyword.lower() in task_data.lower():
        result_msg = f"Keyword '{keyword}' found in input!"
        logger.info(f"Celery Task {self.request.id}: {result_msg}")
    else:
        result_msg = "No keyword detected."
        logger.info(f"Celery Task {self.request.id}: No special word found.")

    logger.info(f"Celery Task {self.request.id} finished")
    return result_msg
