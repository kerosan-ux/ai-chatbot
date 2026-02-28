from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are a helpful assistant for Mike's Barbershop.
Business hours: Mon-Sat 9am-7pm, Sunday closed.
Services: Haircut $20, Beard trim $15, Full combo $30.
Location: 123 Main Street, Bucharest.
Always be friendly, short and helpful. If you don't know something, tell the customer to call us at 0722 000 000.
"""

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(data: Message):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": data.message}
        ]
    )
    return {"reply": response.content[0].text}

@app.get("/widget.js")
async def widget():
    return FileResponse("widget.js", media_type="application/javascript")