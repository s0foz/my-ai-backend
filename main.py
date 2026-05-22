from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ADMIN_PASSWORD = "your-secret-password"
GROQ_API_KEY = "your-groq-api-key-here"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/")
async def root():
    return {"status": "AI backend is running!"}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    messages = req.history + [{"role": "user", "content": req.message}]
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gemma2-9b-it",
                    "messages": messages,
                    "max_tokens": 1024
                }
            )
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        with open("training_data.jsonl", "a") as f:
            json.dump({
                "timestamp": str(datetime.now()),
                "user": req.message,
                "assistant": reply
            }, f)
            f.write("\n")
    except Exception:
        pass
    return {"response": reply}

@app.get("/admin/logs")
async def get_logs(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        with open("training_data.jsonl") as f:
            return {"logs": f.readlines()}
    except Exception:
        return {"logs": []}

@app.post("/admin/update-personality")
async def update_personality(password: str, prompt: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "Personality updated!", "prompt": prompt}
