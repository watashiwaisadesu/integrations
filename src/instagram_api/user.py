# src/instagram_api/user.py

import requests
import logging

from src.utils.errors_handler import ExternalServiceError

logger = logging.getLogger(__name__)

def get_instagram_user_info(access_token: str) -> dict:
    """
    Retrieve user info (user_id, username, account_type) from the Instagram Graph API.
    """
    url = "https://graph.instagram.com/v21.0/me"
    params = {
        "fields": "user_id,username,account_type",
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        # Network-level error (DNS, connection refused, etc.)
        logger.error(f"Request error while fetching Instagram user info: {e}")
        raise ExternalServiceError("Failed to communicate with Instagram Graph endpoint") from e

    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Instagram user info: {data}")
        return data
    else:
        logger.error(f"Failed to get user info (HTTP {response.status_code}): {response.text}")
        raise ExternalServiceError(
            f"Failed to get user info (HTTP {response.status_code}): {response.text}"
        )


def get_instagram_media(instagram_id: str, access_token: str) -> dict:
    """
    Retrieve media data for a given Instagram ID from the Instagram Graph API.
    """
    url = f"https://graph.instagram.com/v21.0/{instagram_id}/media"
    params = {
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching Instagram media: {e}")
        raise ExternalServiceError("Failed to communicate with Instagram Graph endpoint") from e

    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Instagram media data: {data}")
        return data
    else:
        logger.error(f"Failed to get media data (HTTP {response.status_code}): {response.text}")
        raise ExternalServiceError(
            f"Failed to get media data (HTTP {response.status_code}): {response.text}"
        )
