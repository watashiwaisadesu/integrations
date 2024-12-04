from celery import Celery
from src.core.config import REDIS
celery = Celery(
    "integrations_setup",
    broker=REDIS,
    backend=REDIS,
)

celery.autodiscover_tasks(["src.tasks.webhook_setup_task"])
