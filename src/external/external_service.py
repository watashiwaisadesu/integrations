from fastapi import FastAPI, HTTPException, Request
import logging

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Example in-memory storage to simulate processing
processed_messages = {}


@app.post("/process")
async def process_message(request: Request):
    """
    Endpoint to receive messages, process them, and return a response.
    """
    try:
        # Parse the incoming message payload
        payload = await request.json()
        logging.info(f"Received message for processing: {payload}")

        page_id = payload.get("page_id")
        sender_id = payload.get("sender_id")
        message_text = payload.get("message_text")

        if not page_id or not sender_id or not message_text:
            raise HTTPException(status_code=400, detail="Missing required fields in payload")

        # Simulate processing (e.g., NLP, database lookup, etc.)
        response_text = f"Processed message: {message_text[::-1]}"  # Reverse the text as a demo

        # Store in memory (for demo purposes)
        processed_messages[sender_id] = {
            "page_id": page_id,
            "message_text": message_text,
            "response_text": response_text,
        }

        # Respond with the processed message
        return {"status": "success", "reply": response_text}

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Error processing the message")


@app.get("/history/{sender_id}")
async def get_message_history(sender_id: str):
    """
    Endpoint to retrieve processed message history for a given sender.
    """
    history = processed_messages.get(sender_id)
    if not history:
        raise HTTPException(status_code=404, detail="No history found for this sender")
    return {"status": "success", "history": history}
