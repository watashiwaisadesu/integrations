import requests
import logging

from src.utils.errors_handler import ExternalServiceError


logger = logging.getLogger(__name__)


class InstagramAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_short_access_token(self, code):
        """
        Exchange the authorization code for a short-lived access token.
        """
        url = 'https://api.instagram.com/oauth/access_token'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': code
        }


        try:
            response = requests.post(url, data=payload)
        except requests.exceptions.RequestException as e:
            # Catches any network-level error (connection refused, DNS failure, etc.)
            logger.error(f"Request error while fetching short-lived token: {e}")
            raise ExternalServiceError("Failed to communicate with Instagram OAuth endpoint") from e

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Short Access Token Response: {data}")
            return data.get("access_token")
        else:
            logger.error(f"Error fetching short-lived token: {response.status_code}, {response.text}")
            raise ExternalServiceError(
                f"Error fetching short-lived token (HTTP {response.status_code}): {response.text}"
            )


    def get_long_lived_access_token(self, short_lived_token: str) -> str:
        """
        Exchange a short-lived token for a long-lived access token.
        """
        url = "https://graph.instagram.com/access_token"
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": self.client_secret,
            "access_token": short_lived_token,
        }

        try:
            response = requests.get(url, params=params)
            print(response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while fetching long-lived token: {e}")
            raise ExternalServiceError("Failed to communicate with Instagram Graph endpoint") from e

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Long-Lived Access Token Response: {data}")
            return data.get("access_token")
        else:
            logger.error(f"Error fetching long-lived token: {response.status_code}, {response.text}")
            raise ExternalServiceError(
                f"Error fetching long-lived token (HTTP {response.status_code}): {response.text}"
            )


    def refresh_long_lived_token(self, long_lived_access_token: str) -> str:
        """
        Refresh a long-lived access token.
        """
        url = "https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": long_lived_access_token,
        }

        try:
            response = requests.get(url, params=params)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while refreshing long-lived token: {e}")
            raise ExternalServiceError("Failed to communicate with Instagram Graph endpoint") from e

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"Refreshed Token Response: {data}")
            return data.get("access_token")
        else:
            logger.error(f"Error refreshing long-lived token: {response.status_code}, {response.text}")
            raise ExternalServiceError(
                f"Error refreshing long-lived token (HTTP {response.status_code}): {response.text}"
            )
