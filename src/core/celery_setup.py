from celery import Celery

celery = Celery(
    "integrations_setup",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery.autodiscover_tasks(["src.tasks.webhook_setup_task"])
