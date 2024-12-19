import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.telegram_api.schemas import PhoneNumberRequest, VerificationCodeRequest, TelegramAppSchema
from src.core.database_setup import get_async_db
from src.telegram_api.service import (
    request_code_service,
    submit_code_service
)
from src.db.repositories.telegram_app_repositories import set_telegram_app


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

telegram_api_router = APIRouter()


@telegram_api_router.post("/set-app/")
async def set_telegram_app(data: TelegramAppSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Set or update the Telegram app (api_id and api_hash).
    """
    app = await set_telegram_app(api_id=data.api_id, api_hash=data.api_hash, db=db)
    return {"status": "App set successfully", "app": {"api_id": app.api_id, "api_hash": app.api_hash}}


@telegram_api_router.post("/request-code/")
async def request_code(data: PhoneNumberRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Request a login code for a given phone number.
    """
    try:
        result = await request_code_service(phone_number=data.phone_number, db=db)
        return {"status": "Code sent", "phone_code_hash": result["phone_code_hash"]}
    except Exception as e:
        logging.error(f"Error requesting code for {data.phone_number}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send code.")


@telegram_api_router.post("/submit-code/")
async def submit_code(data: VerificationCodeRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Submit the received verification code and complete the login process.
    """
    try:
        result = await submit_code_service(phone_number=data.phone_number, code=data.code, db=db)
        return {"status": "Logged in successfully", "session": result["session"]}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error submitting code for {data.phone_number}: {e}")
        raise HTTPException(status_code=500, detail="Failed to log in.")
