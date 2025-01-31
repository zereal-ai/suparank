from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from .suparank import Suparank
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Initialize Suparank
token = os.getenv("AIRTABLE_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")

if not token or not base_id:
    raise ValueError("AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in environment variables")

suparank = Suparank(token)
suparank.set_base(base_id)

class EntryCreate(BaseModel):
    title: str
    description: str

class ComparisonChoice(BaseModel):
    winner_id: str
    loser_id: str

@app.get("/api/next-pair")
async def get_next_pair():
    pair = suparank.get_next_pair()
    if not pair:
        return {"message": "Ranking complete", "complete": True}
    return {"pair": pair, "complete": False}

@app.post("/api/choose")
async def choose_winner(choice: ComparisonChoice):
    try:
        suparank.choose_winner(choice.winner_id, choice.loser_id)
        return {"message": "Choice recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rankings")
async def get_rankings():
    return {"rankings": suparank.get_rankings()}

@app.post("/api/entries")
async def add_entry(entry: EntryCreate):
    try:
        new_entry = suparank.add_entry(entry.title, entry.description)
        return {"entry": new_entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 