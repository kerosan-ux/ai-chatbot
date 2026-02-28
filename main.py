from fastapi import FastAPI, HTTPException
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

# Each client has a unique ID and their own config
CLIENTS = {
    "mikes-barbershop": {
        "name": "Mike's Barbershop",
        "prompt": """You are a helpful assistant for Mike's Barbershop.
Business hours: Mon-Sat 9am-7pm, Sunday closed.
Services: Haircut $20, Beard trim $15, Full combo $30.
Location: 123 Main Street, Bucharest.
Always be friendly, short and helpful. If you don't know something, tell the customer to call us at 0722 000 000."""
    },
    "fitness-zone": {
        "name": "Fitness Zone Gym",
        "prompt": """You are a helpful assistant for Fitness Zone Gym.
Business hours: Mon-Fri 6am-10pm, Sat-Sun 8am-8pm.
Memberships: Monthly $40, Annual $350, Day pass $10.
Location: 456 Sport Avenue, Bucharest.
Always be energetic, friendly and helpful. If you don't know something, tell the customer to call us at 0733 000 000."""
    }
}

class Message(BaseModel):
    message: str
    client_id: str

@app.post("/chat")
async def chat(data: Message):
    client_config = CLIENTS.get(data.client_id)
    if not client_config:
        raise HTTPException(status_code=404, detail="Client not found")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=client_config["prompt"],
        messages=[
            {"role": "user", "content": data.message}
        ]
    )
    return {"reply": response.content[0].text}

@app.get("/widget.js")
async def widget():
    return FileResponse("widget.js", media_type="application/javascript")

@app.get("/clients")
async def list_clients():
    return [{"id": k, "name": v["name"]} for k, v in CLIENTS.items()]