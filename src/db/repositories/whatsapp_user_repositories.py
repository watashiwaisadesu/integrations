from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.db.models.whatsapp_models import WhatsAppUser
from sqlalchemy.ext.asyncio import AsyncSession


def create_or_update_whatsapp_user(
    db: Session,
    api_url: str,
    id_instance: str,
    api_token: str,
    callback_url: str,
    order_id: str
):
    """
    Create a new WhatsApp user or update the existing user if id_instance already exists.

    Args:
        db (Session): SQLAlchemy sync database session.
        api_url (str): URL for the WhatsApp API.
        id_instance (str): Unique ID for the WhatsApp instance.
        api_token (str): Token for WhatsApp API authentication.
        callback_url (str): Bot callback URL.
        order_id (str): Order ID.

    Returns:
        WhatsAppUser: The created or updated WhatsApp user object.
    """
    try:
        # Check if the user with id_instance already exists
        result = db.execute(
            select(WhatsAppUser).where(WhatsAppUser.id_instance == id_instance)
        )
        user = result.scalars().first()

        if user:
            # Update existing user's data
            user.api_url = api_url
            user.api_token = api_token
            user.bot_url = callback_url
            user.order_id = order_id
        else:
            # Create a new user
            user = WhatsAppUser(
                api_url=api_url,
                id_instance=id_instance,
                api_token=api_token,
                bot_url=callback_url,
                authorized=False,
                order_id=order_id,
            )
            db.add(user)

            # Commit changes (either update or insert)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error while creating or updating user with id_instance '{id_instance}': {e}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error: {e}")


async def get_whatsapp_user(db: AsyncSession, id_instance: int):
    """
    Retrieve a WhatsApp user from the database based on id_instance, api_token,
    callback_url, and order_id.

    Args:
        db (AsyncSession): SQLAlchemy async database session.
        id_instance (str): Unique ID for the WhatsApp instance.
        api_token (str): Token for WhatsApp API authentication.
        callback_url (str): Bot callback URL.
        order_id (str): Order ID.

    Returns:
        WhatsAppUser | None: The WhatsApp user object if found, else None.
    """
    try:
        # Asynchronous query to fetch a WhatsApp user
        result = await db.execute(
            select(WhatsAppUser).where(
                WhatsAppUser.id_instance == id_instance,
            )
        )
        user = result.scalars().first()
        return user
    except Exception as e:
        # Log the error if necessary
        print(f"Error retrieving WhatsApp user: {e}")
        return None
