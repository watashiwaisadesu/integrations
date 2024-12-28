from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Data Models
class MessagingObject(BaseModel):
    sender: dict
    recipient: dict
    timestamp: int
    message: dict


class EntryObject(BaseModel):
    id: str
    time: int
    messaging: list[MessagingObject]


class WebhookObject(BaseModel):
    object: str
    entry: list[EntryObject]


class AppSetupRequest(BaseModel):
    email: EmailStr = Field(..., description="Email of the existing Facebook account.")
    password: str = Field(..., description="Password of the existing Facebook account.")
    verify_token: str = Field(..., description="Random token used to verify incoming webhook requests.")
    app_name: str = Field(..., description="Name of the existing app to set up the webhook for.")



