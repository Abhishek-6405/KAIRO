from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

KAIRO_PERSONALITY = """
You are KAIRO, a highly intelligent personal AI assistant created by Abhishek.
You are helpful, sharp, and to the point.
You assist Abhishek with anything he asks — answering questions, finding information, controlling his PC, and more.
Always address him as Abhishek.
Keep responses clear and concise.
"""

class MessageRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "KAIRO is online", "model": MODEL_NAME}

@app.post("/chat")
def chat(request: MessageRequest):
    full_prompt = f"{KAIRO_PERSONALITY}\n\nAbhishek: {request.message}\nKAIRO:"
    
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    })
    
    data = response.json()
    print("RAW RESPONSE:", data)  # this will show us exactly what Ollama returns
    
    reply = data.get("response") or data.get("message", {}).get("content", "")
    return {
        "response": reply.strip()
    }