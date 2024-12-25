from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.openai.schemas import UserCreate, TokenUsage
from src.db.models.openai_models import User
from src.core.database_setup import get_async_db
# import tiktoken

# FastAPI app
app = FastAPI()

# Simulate $10 = 10,000 tokens
DOLLAR_TO_TOKENS = 1000  # 1 dollar = 1000 tokens

@app.post("/register/")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter(User.username == user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Calculate tokens based on the amount paid
    tokens = int(user.paid_amount * DOLLAR_TO_TOKENS)
    new_user = User(username=user.username, paid_amount=user.paid_amount, remaining_tokens=tokens)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully", "username": new_user.username, "tokens": new_user.remaining_tokens}

@app.post("/use_tokens/")
async def use_tokens(usage: TokenUsage, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter(User.username == usage.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.remaining_tokens < usage.tokens_used:
        raise HTTPException(status_code=400, detail="Insufficient tokens")

    # Deduct tokens
    user.remaining_tokens -= usage.tokens_used
    db.add(user)
    await db.commit()
    return {"message": "Tokens used successfully", "remaining_tokens": user.remaining_tokens}

@app.get("/get_user/{username}")
async def get_user(username: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "paid_amount": user.paid_amount,
        "remaining_tokens": user.remaining_tokens,
    }
#
# async def count_tokens(prompt: str, model: str = "gpt-4") -> int:
#     encoding = tiktoken.encoding_for_model(model)
#     return len(encoding.encode(prompt))
