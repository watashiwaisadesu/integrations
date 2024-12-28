from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.core.database_setup import get_async_db
from src.bots.openai.service import create_assistant_in_openai
from src.db.repositories.instagram_user_repositories import (
    get_instagram_account_user_by_id,
    update_instagram_bot_id
)
from src.db.repositories.telegram_user_repositories import get_telegram_user_by_id, update_telegram_bot_id
from src.db.repositories.whatsapp_user_repositories import (
    get_whatsapp_user_by_id,
    update_whatsapp_user_bot_id
)

logger = logging.getLogger(__name__)


bot_router = APIRouter()


@bot_router.get("/bot_creation/{platform}/{user_id}", response_class=HTMLResponse)
async def show_bot_creation_form(platform: str, user_id: str):
    """
    Render a bot creation form for the specified platform and user.
    """
    html_content = f"""
    <html>
        <body>
            <h1>Create Bot for platform={platform}, user_id={user_id}</h1>
            <form action="/v1/bot/bot_creation/{platform}/{user_id}" method="post">
                <label>Creativity: <input type="text" name="creativity" value="0.7" /></label><br/>
                <label>Instructions: <input type="text" name="instructions" value="Be polite" /></label><br/>
                <button type="submit">Create Bot</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@bot_router.post("/bot_creation/{platform}/{user_id}")
async def create_bot_for_user(
    platform: str,
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
):
    form_data = await request.form()
    creativity_str = form_data.get("creativity", "0.7")
    instructions = form_data.get("instructions", "Be polite")

    try:
        creativity = float(creativity_str)
        if not (0.0 <= creativity <= 1.0):
            raise ValueError("Creativity must be between 0.0 and 1.0")
    except ValueError as ve:
        logger.error(f"Invalid creativity value: {creativity_str}")
        raise HTTPException(status_code=400, detail="Invalid creativity value. Must be a float between 0.0 and 1.0") from ve

    try:
        # Fetch user based on the platform
        if platform == "instagram":
            user = await get_instagram_account_user_by_id(db, user_id)
        elif platform == "telegram":
            user = await get_telegram_user_by_id(db, user_id)
        elif platform == "whatsapp":
            user = await get_whatsapp_user_by_id(db, str(user_id))
        else:
            raise HTTPException(status_code=400, detail="Invalid platform. Must be 'instagram' or 'telegram'.")
        logger.info(f"Fetched user: {user}")
    except Exception as e:
        logger.error(f"Error fetching user for platform={platform}, user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user.")
    if not user:
        logger.error(f"User with user_id={user_id} not found for platform={platform}")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        assistant_id = create_assistant_in_openai(
            name=f"My {platform} Bot",
            instructions=instructions,
            creativity=creativity,
        )
        logger.info(f"Assistant created with ID: {assistant_id}")
    except Exception as e:
        logger.error(f"Failed to create assistant: {e}")
        raise HTTPException(status_code=500, detail="Failed to create assistant")

    try:
        # Update the user's bot ID in the database based on the platform
        if platform == "instagram":
            success = await update_instagram_bot_id(db, user_id, assistant_id)
        elif platform == "telegram":
            success = await update_telegram_bot_id(db, user_id, assistant_id)
        elif platform == "whatsapp":
            success = await update_whatsapp_user_bot_id(db, str(user_id), assistant_id)
        else:
            success = False
        logger.info(f"Updated bot ID for platform={platform}, user_id={user_id}, success={success}")
    except Exception as e:
        logger.error(f"Failed to update bot ID for platform={platform}, user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update bot ID")

    if not success:
        logger.error(f"Failed to update bot ID for user_id={user_id} on platform={platform}")
        raise HTTPException(status_code=500, detail="Failed to update bot ID")

    logger.info(
        f"Assistant created for user_id={user_id}, platform={platform}, with assistant_id={assistant_id}, "
        f"creativity={creativity}, instructions={instructions}"
    )

    return {
        "user_id": user_id,
        "platform": platform,
        "assistant_id": assistant_id,
        "creativity": creativity,
        "instructions": instructions,
        "status": "success",
    }

