from pydantic import BaseModel

# API Models
class PhoneNumberRequest(BaseModel):
    phone_number: str

class VerificationCodeRequest(BaseModel):
    phone_number: str
    code: str

class TelegramAppSchema(BaseModel):
    api_id: str
    api_hash: str