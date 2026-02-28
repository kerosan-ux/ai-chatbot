from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import requests
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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

class Lead(BaseModel):
    name: str
    email: str
    client_id: str

@app.get("/")
async def landing():
    return FileResponse("landing.html")

@app.post("/chat")
async def chat(data: Message):
    client_config = CLIENTS.get(data.client_id)
    if not client_config:
        raise HTTPException(status_code=404, detail="Client not found")

    response = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=client_config["prompt"],
        messages=[
            {"role": "user", "content": data.message}
        ]
    )
    return {"reply": response.content[0].text}

@app.post("/leads")
async def save_lead(data: Lead):
    if not CLIENTS.get(data.client_id):
        raise HTTPException(status_code=404, detail="Client not found")

    requests.post(
        f"{SUPABASE_URL}/rest/v1/leads",
        json={
            "name": data.name,
            "email": data.email,
            "client_id": data.client_id
        },
        headers=HEADERS
    )
    return {"success": True}

@app.get("/leads/{client_id}")
async def get_leads(client_id: str):
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?client_id=eq.{client_id}&select=*&order=created_at.desc",
        headers=HEADERS
    )
    return res.json()

@app.get("/leads-all")
async def get_all_leads(password: str):
    if password != os.getenv("ADMIN_PASSWORD"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads?select=*&order=created_at.desc",
        headers=HEADERS
    )
    return res.json()

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return FileResponse("admin.html")

@app.get("/widget.js")
async def widget():
    return FileResponse("widget.js", media_type="application/javascript")