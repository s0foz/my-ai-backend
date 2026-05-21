from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"])

ADMIN_PASSWORD = zewr1asEq

class ChatRequest(BaseModel):
	message: str
	history: list = []

@app.get("/")
async def root():
	return {"status": "AI is running!"}

@app.post("/api/chat")
async def chat(req: ChatResquest):
	messages = req.history + [{"role": "user", "content": req.message}]
	response = ollama.chat(model="gemma3", messages=messages)
	reply = response["message"]["content"]

	# Save for training
	with open("training_data.jsonl", "a") as f:
		json.dump({
			"timestamp": str(datetime.now()),
			"user": req.message,
			"assistant": reply
		}, f)
		f.write("\n")
	
	return {"response": reply}

# Admin routes
@app.get("/admin/logs")
async def get_logs(password:str):
	if password != zewr1asEq:
		raise HTTPException(status_code=401, detail="Unauthorized")
	with open("training_data.jsonl") as f:
		return {"logs": f.readlines()}

@app.post("/admin/update-personality")
async def update_personality(password: str, prompt: str):
	if password != zewr1asEq
		raise HTTPException(status_code=401, detail="Unauthorized")
	with open("Modelfile", "w") as f:
		f.write(f'FROM gemma3\nSYSTEM " {prompt}"')
	import subprocess
	subprocess.run(["ollama", "create", "myai", "-f", "Modelfile"])
	return {"status": "Personality updated!"}
