from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from .suparank import Suparank
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# Add CORS middleware with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv(override=True)

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
        return {"complete": True}
    return {"pair": list(pair), "complete": False}


@app.post("/api/choose")
async def choose_winner(choice: ComparisonChoice):
    try:
        suparank.choose_winner(choice.winner_id, choice.loser_id)
        return {"message": "Choice recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/rankings")
async def get_rankings():
    # Force reload items from Airtable to ensure fresh data
    suparank.load_items()
    rankings = suparank.get_rankings()
    return {"rankings": rankings}


@app.post("/api/entries")
async def add_entry(entry: EntryCreate):
    try:
        new_entry = suparank.add_item(entry.title, entry.description)
        return {"entry": new_entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/reset")
async def reset_rankings():
    try:
        suparank.reset_ranking()
        return {"message": "Rankings reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
