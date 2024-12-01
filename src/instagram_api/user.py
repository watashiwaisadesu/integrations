import requests

def get_instagram_user_info(access_token):
    # Define the endpoint and parameters
    url = "https://graph.instagram.com/v21.0/me"
    params = {
        "fields": "user_id,username,account_type",  # Request the user_id and username fields
        "access_token": access_token  # Pass the access token
    }

    # Send the GET request to retrieve user info
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        user_info = response.json()
        print(f"USERRRR:{user_info}")
        return user_info
    else:
        raise Exception(f"Failed to get user info. Status code: {response.status_code}, Response: {response.text}")


def get_instagram_media(instagram_id, access_token):
    # Define the endpoint and parameters
    url = f"https://graph.instagram.com/v21.0/{instagram_id}/media"
    params = {
        "access_token": access_token  # Pass the access token
    }

    # Send the GET request to retrieve media
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        media_data = response.json()
        return media_data
    else:
        raise Exception(f"Failed to get media data. Status code: {response.status_code}, Response: {response.text}")


