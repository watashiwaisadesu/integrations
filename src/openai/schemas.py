from pydantic import BaseModel

# Schemas
class UserCreate(BaseModel):
    username: str
    paid_amount: float

class TokenUsage(BaseModel):
    username: str
    tokens_used: int
