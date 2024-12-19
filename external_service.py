from fastapi import FastAPI, HTTPException, Request
import logging

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Example in-memory storage to simulate processing
processed_messages = {}


@app.post("/username/bot/1000")
async def process_message(request: Request):
    """
    Endpoint to receive messages, process them, and return a response.
    """
    try:
        # Parse the incoming message payload
        payload = await request.json()
        logging.info(f"Received message for processing: {payload}")

        platform = payload.get("platform")
        message_text = payload.get("message_text")

        if not platform or not message_text:
            raise HTTPException(status_code=400, detail="Missing required fields in payload")

        # Simulate processing (e.g., NLP, database lookup, etc.)
        response_text = f"Processed message on {platform}: {message_text[::-1]}"  # Reverse the text as a demo

        # Store in memory (for demo purposes)
        processed_messages[message_text] = {
            "platform": platform,
            "message_text": message_text,
            "response_text": response_text,
        }

        # Respond with the processed message
        json = {"status": "success", "reply": response_text}
        print(f"Return back: {json}")
        return json

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Error processing the message")


