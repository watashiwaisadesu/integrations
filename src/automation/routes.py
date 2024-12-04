from fastapi import  HTTPException, APIRouter, Request
from pydantic import BaseModel, EmailStr, Field
from src.tasks.webhook_setup_task import webhook_setup_task

class WebhookSetupRequest(BaseModel):
    email: EmailStr = Field(..., description="Email of the existing Facebook account.")
    password: str = Field(..., description="Password of the existing Facebook account.")
    verify_token: str = Field(..., description="Random token used to verify incoming webhook requests.")
    app_name: str = Field(..., description="Name of the existing app to set up the webhook for.")

webhook_settings_router = APIRouter()

@webhook_settings_router.post("/webhook-setup")
def webhook_setup(request: Request, body: WebhookSetupRequest):
    try:
        # Retrieve the base URL from the request object
        callback_url = str(request.base_url)
        print(callback_url)

        # Queue the task with the generated callback_url
        task = webhook_setup_task.delay(
            body.email,
            body.password,
            body.verify_token,
            callback_url,
            body.app_name
        )
        return {"status": "Task queued", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


