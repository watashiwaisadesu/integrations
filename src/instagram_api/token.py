import requests


def get_short_access_token(client_id, client_secret, redirect_uri, code):
    url = 'https://api.instagram.com/oauth/access_token'

    # Prepare the payload
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    }

    # Send the POST request to get the access token
    response = requests.post(url, data=payload)
    print(f"RRR:{response.json()}")
    # Check for a successful response
    if response.status_code == 200:
        print(f"RRR:Success")
        return response.json()['access_token']  # Return the response as a JSON (it will contain the access token)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_long_lived_access_token(short_lived_token, client_secret):

    url = "https://graph.instagram.com/access_token"

    # Parameters for the API request
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': client_secret,
        'access_token': short_lived_token
    }

    # Make the request to exchange the short-lived token for a long-lived one
    response = requests.get(url, params=params)
    print(f"SHOORT:{response.json()['access_token']}")
    # Check if the response is successful
    if response.status_code == 200:
        print(f"SHOORT:{response.json()['access_token']}")
        return response.json()['access_token']
    else:
        return {"error": "Failed to get long-lived token", "status_code": response.status_code,
                "response": response.text}


def refresh_long_lived_token(long_lived_access_token):
    # Define the endpoint and parameters
    url = "https://graph.instagram.com/refresh_access_token"
    params = {
        "grant_type": "ig_refresh_token",
        "access_token": long_lived_access_token
    }
    # Send the GET request to refresh the token
    response = requests.get(url, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        print(f"LOONG:{response.json()['access_token']}")
        return response.json()
    else:
        raise Exception(f"Failed to refresh token. Status code: {response.status_code}, Response: {response.text}")



