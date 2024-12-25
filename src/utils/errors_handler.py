from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Any, Callable

class BaseException(Exception):
    """Base class for all exceptions."""
    pass

class VerificationTokenMismatch(BaseException):
    """Verification token mismatch"""
    pass

class InvalidWebhookPayload(BaseException):
    """Invalid webhook payload"""
    pass

class InternalServerError(BaseException):
    """Internal server error"""
    pass

class InvalidQueryParameter(BaseException):
    """Invalid or missing query parameter."""
    pass

class ExternalServiceError(BaseException):
    """External service communication error"""
    pass

class TelegramMessageHandlingError(BaseException):
    """Error occurred while handling a Telegram message."""
    pass




def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BaseException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        VerificationTokenMismatch,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Verification token mismatch",
                "error_code": "verification_token_mismatch",
            },
        ),
    )

    app.add_exception_handler(
        InvalidWebhookPayload,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid webhook payload",
                "error_code": "invalid_webhook_payload",
            },
        ),
    )

    app.add_exception_handler(
        InternalServerError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Internal server error",
                "error_code": "internal_server_error",
            },
        ),
    )

    app.add_exception_handler(
        ExternalServiceError,
        create_exception_handler(
            status_code=status.HTTP_502_BAD_GATEWAY,  # or HTTP_503_SERVICE_UNAVAILABLE
            initial_detail={
                "message": "Failed to communicate with external service",
                "error_code": "external_service_error",
            },
        ),
    )

    app.add_exception_handler(
        InvalidQueryParameter,
        create_exception_handler(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,  # or status.HTTP_400_BAD_REQUEST
            initial_detail={
                "message": "Invalid query parameter",
                "error_code": "invalid_query_parameter",
            },
        ),
    )

    app.add_exception_handler(
        TelegramMessageHandlingError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "Error occurred while handling a Telegram message",
                "error_code": "telegram_message_handling_error",
            },
        ),
    )
