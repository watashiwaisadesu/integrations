from pydantic import BaseModel, EmailStr, Field

class CreateInstanceRequest(BaseModel):
    email: EmailStr = Field(..., description="Email of the existing GreenAPI account.")
    password: str = Field(..., description="Password of the existing GreenAPI account.")

