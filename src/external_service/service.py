import httpx



async def create_bot_request(username: str, external_url, debug_mode: bool = False) -> str:
    """
    Sends a request to an external service to create a bot for the user.
    Returns the bot URL if successful, or None if the request fails.
    """

    payload = {"username": username}
    if debug_mode:
        return f"{external_url}/username/bot/1000"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(external_url, json=payload)
            response.raise_for_status()
            data = response.json()
            bot_url = data.get("bot_url")  # Assuming the response contains 'bot_url'
            if not bot_url:
                raise ValueError("Bot URL is missing in the response.")
            return bot_url
        except Exception as e:
            # Log the error
            print(f"Error creating bot: {e}")
            return None


def create_bot_request_sync(username: str, external_url, debug_mode: bool = False) -> str:
    """
    Sends a request to an external service to create a bot for the user.
    Returns the bot URL if successful, or None if the request fails.
    """
    payload = {"username": username}
    if debug_mode:
        return f"{external_url}/username/bot/1000"

    try:
        with httpx.Client() as client:
            response = client.post(external_url, json=payload)
            response.raise_for_status()
            data = response.json()
            bot_url = data.get("bot_url")  # Assuming the response contains 'bot_url'
            if not bot_url:
                raise ValueError("Bot URL is missing in the response.")
            return bot_url
    except Exception as e:
        # Log the error
        print(f"Error creating bot: {e}")
        return None