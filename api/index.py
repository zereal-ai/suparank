from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from .suparank import Suparank
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

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
load_dotenv(override=True)

# Initialize Suparank
token = os.getenv("AIRTABLE_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")

print(f"Debug - Token length: {len(token) if token else 0}")
print(f"Debug - Base ID: {base_id}")

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
    debug_info = suparank.get_debug_info()
    print("\n".join(debug_info))  # Print debug info to terminal
    if not pair:
        return {"message": "Ranking complete", "complete": True}
    return {"pair": pair, "complete": False}

@app.post("/api/choose")
async def choose_winner(choice: ComparisonChoice):
    try:
        suparank.choose_winner(choice.winner_id, choice.loser_id)
        debug_info = suparank.get_debug_info()
        print("\n".join(debug_info))  # Print debug info to terminal
        return {"message": "Choice recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rankings")
async def get_rankings():
    # Force reload entries from Airtable to ensure fresh data
    suparank.load_entries()
    rankings = suparank.get_rankings()
    debug_info = suparank.get_debug_info()
    print("\n".join(debug_info))  # Print debug info to terminal
    return {"rankings": rankings}

@app.post("/api/entries")
async def add_entry(entry: EntryCreate):
    try:
        new_entry = suparank.add_entry(entry.title, entry.description)
        debug_info = suparank.get_debug_info()
        print("\n".join(debug_info))  # Print debug info to terminal
        return {"entry": new_entry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reset")
async def reset_rankings():
    try:
        suparank.reset_ranking()
        debug_info = suparank.get_debug_info()
        print("\n".join(debug_info))  # Print debug info to terminal
        return {"message": "Rankings reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 