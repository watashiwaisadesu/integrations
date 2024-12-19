from fastapi import APIRouter, Depends
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database_setup import get_async_db
from src.db.repositories.external_service_app_repositories import set_app_external_service_base_url


logging.basicConfig(level=logging.INFO)

external_service_api_router = APIRouter()


@external_service_api_router.post("/set_external_service_base_url")
async def set_external_service_base_url(
        external_service_base_url: str,
        db: AsyncSession = Depends(get_async_db)
):
    await set_app_external_service_base_url(db, external_service_base_url)