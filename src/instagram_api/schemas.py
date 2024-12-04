from pydantic import BaseModel
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

