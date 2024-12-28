import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from sqlalchemy.ext.asyncio import AsyncSession

from src.messengers.telegram_api.schemas import PhoneNumberRequest, VerificationCodeRequest, TelegramAppSchema
from src.core.database_setup import get_async_db
from src.messengers.telegram_api.service import (
    request_code_service,
    submit_code_service
)
from src.db.repositories.telegram_app_repositories import set_telegram_app

from src.utils.errors_handler import (
    InternalServerError,
    InvalidQueryParameter,
)

logger = logging.getLogger(__name__)

telegram_api_router = APIRouter()


@telegram_api_router.post("/set-app/")
async def set_telegram_app_route(data: TelegramAppSchema, db: AsyncSession = Depends(get_async_db)):
    """
    Set or update the Telegram app (api_id and api_hash).
    """
    try:
        app = await set_telegram_app(api_id=data.api_id, api_hash=data.api_hash, db=db)
        return {
            "status": "App set successfully",
            "app": {"api_id": app.api_id, "api_hash": app.api_hash}
        }
    except Exception as e:
        logger.error(f"Unhandled error in set_telegram_app: {e}")
        # Raise a 500-level error, or define your own custom exception
        raise InternalServerError("Failed to set Telegram app.")


@telegram_api_router.post("/request-code/")
async def request_code_route(
    data: PhoneNumberRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Request a login code for a given phone number.
    """
    try:
        result = await request_code_service(phone_number=data.phone_number, db=db)
        return {"status": "Code sent", "phone_code_hash": result["phone_code_hash"]}
    except ValueError as ve:
        logger.error(f"ValueError requesting code for {data.phone_number}: {ve}")
        # If you consider invalid phone numbers or similar as an invalid query:
        raise InvalidQueryParameter(str(ve))
    except Exception as e:
        logger.error(f"Error requesting code for {data.phone_number}: {e}")
        # Instead of HTTPException(500, ...):
        raise InternalServerError("Failed to send code.")


@telegram_api_router.post("/submit-code/")
async def submit_code_route(
    data: VerificationCodeRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Submit the received verification code and complete the login process.
    """
    try:
        user_id  = await submit_code_service(
            phone_number=data.phone_number,
            code=data.code,
            db=db
        )
        base_url = f"https://{request.base_url.netloc}"
        creation_link = f"{base_url}/v1/bot/bot_creation/telegram/{user_id}"
        return RedirectResponse(url=creation_link, status_code=302)
    except ValueError as ve:
        # If the code is invalid, handle with a 400/422:
        logger.error(f"ValueError submitting code for {data.phone_number}: {ve}")
        raise InvalidQueryParameter(str(ve))
    except Exception as e:
        logger.error(f"Error submitting code for {data.phone_number}: {e}")
        # Instead of HTTPException(500, detail=...):
        raise InternalServerError("Failed to log in.")
