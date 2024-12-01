from fastapi import  HTTPException, APIRouter
from pydantic import EmailStr
from src.tasks.webhook_setup_task import webhook_setup_task

webhook_setup_router = APIRouter()

@webhook_setup_router.post("/webhook-setup")
def webhook_setup(email: EmailStr, password: str, verify_token: str, callback_url: str, app_name: str):
    try:
        task = webhook_setup_task.delay(email, password, verify_token, callback_url, app_name)
        return {"status": "Task queued", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


