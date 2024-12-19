from celery import Celery
from src.core.config import REDIS
celery = Celery(
    "integrations_setup",
    broker=REDIS,
    backend=REDIS,
)

celery.autodiscover_tasks(["src.tasks.app_setup_task"])
celery.autodiscover_tasks(["src.tasks.create_instance_task"])
