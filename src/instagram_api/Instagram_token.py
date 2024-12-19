import requests


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

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print(f"Short Access Token Response: {response.json()}")
            return response.json().get('access_token')
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def get_long_lived_access_token(self, short_lived_token):
        """
        Exchange a short-lived token for a long-lived access token.
        """
        url = "https://graph.instagram.com/access_token"
        params = {
            'grant_type': 'ig_exchange_token',
            'client_secret': self.client_secret,
            'access_token': short_lived_token
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            print(f"Long-Lived Access Token Response: {response.json()}")
            return response.json().get('access_token')
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def refresh_long_lived_token(self, long_lived_access_token):
        """
        Refresh a long-lived access token.
        """
        url = "https://graph.instagram.com/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": long_lived_access_token
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            print(f"Refreshed Token Response: {response.json()}")
            return response.json().get('access_token')
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
