from fastapi import FastAPI, HTTPException, Request
import logging
import openai
from src.core.config import OPENAI_API_KEY

from src.utils.middleware import register_middleware

# Инициализируем FastAPI-приложение
app = FastAPI()
register_middleware(app)

# Логирование
logging.basicConfig(level=logging.INFO)

# Пример хранилища (для демонстрации)
processed_messages = {}

# Укажите свой ключ (или используйте переменную окружения)
openai.api_key = OPENAI_API_KEY

@app.post("/username/bot/1000")
async def process_message(request: Request):
    """
    Endpoint для приёма сообщений, обращения к OpenAI и возвращения ответа.
    """
    try:
        # Получаем payload
        payload = await request.json()
        logging.info(f"Received message for processing: {payload}")

        platform = payload.get("platform")
        message_text = payload.get("message_text")

        if not platform or not message_text:
            raise HTTPException(status_code=400, detail="Missing required fields in payload")

        # Формируем контекст для ChatCompletion
        # Подход №1: минималистичный — каждый запрос считается самостоятельным
        # Подход №2: сохранять контекст истории диалога.
        # Здесь для простоты просто один раз вызываем модель с системной инструкцией и user-подсказкой
        messages = [
            {
                "role": "system",
                "content": (
                    "You are actual me a human Islambek. Respond in a natural, human-like way. "
                    "If someone asks 'who are you?', respond: 'I'm Islambek, I'm a seller of books'."
                )
            },
            {
                "role": "user",
                "content": message_text
            }
        ]

        # Запрос к ChatCompletion (модель может быть 'gpt-3.5-turbo' или другая)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        # Извлекаем ответ бота
        response_text = completion.choices[0].message["content"].strip()

        # Сохраняем в памяти (для демо)
        processed_messages[message_text] = {
            "platform": platform,
            "message_text": message_text,
            "response_text": response_text,
        }

        # Формируем ответ
        json_resp = {"status": "success", "reply": response_text}
        logging.info(f"Replying with: {json_resp}")
        return json_resp

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Error processing the message")
