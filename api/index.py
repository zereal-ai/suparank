import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyairtable import Table
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env
load_dotenv()
AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_SESSIONS_TABLE_ID = os.getenv("AIRTABLE_SESSIONS_TABLE_ID")
AIRTABLE_ITEMS_TABLE_ID = os.getenv("AIRTABLE_ITEMS_TABLE_ID")

# Initialize the Airtable Table objects
sessions_table = Table(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_SESSIONS_TABLE_ID)
items_table = Table(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_ITEMS_TABLE_ID)

# Initialize the FastAPI app
app = FastAPI(title="Interactive Merge Sort Service")

# Add CORS middleware to allow all origins and methods (including OPTIONS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------------
# Pydantic models
# ---------------------
class StartSessionInput(BaseModel):
    items: list[str]  # For example: ["three", "four", "two", "one", "five"]

class CompareInput(BaseModel):
    choice: str  # Expected to be "A" or "B"

class ItemInput(BaseModel):
    title: str
    description: str | None = None

# ---------------------
# Helper functions to get/update session state from Airtable
# ---------------------
def get_session_state(session_id: str) -> dict:
    try:
        record = sessions_table.get(session_id)
        state_json = record["fields"].get("state")
        if state_json is None:
            raise ValueError("Session state not found in record.")
        return json.loads(state_json)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not found: {e}")


def update_session_state(session_id: str, state: dict):
    try:
        sessions_table.update(session_id, {"state": json.dumps(state)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {e}")

# ---------------------
# Items API Endpoints
# ---------------------
@app.get("/api/items")
def get_items():
    """Get all items from Airtable"""
    try:
        records = items_table.all()
        return [
            {
                "id": record["id"],
                "title": record["fields"].get("title", ""),
                "description": record["fields"].get("description", "")
            }
            for record in records
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch items: {e}")

@app.post("/api/items")
def create_item(item: ItemInput):
    """Create a new item in Airtable"""
    try:
        fields = {"title": item.title}
        if item.description:
            fields["description"] = item.description
        record = items_table.create(fields)
        return {
            "id": record["id"],
            "title": record["fields"].get("title", ""),
            "description": record["fields"].get("description", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {e}")

@app.delete("/api/items/{item_id}")
def delete_item(item_id: str):
    """Delete an item from Airtable"""
    try:
        items_table.delete(item_id)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {e}")

# ---------------------
# Merge Sort State Helpers
# ---------------------
def initiate_merge_task(state: dict) -> dict:
    """
    If no merge is in progress and there are at least two sublists in the work_list,
    remove the first two and create a current merge task.
    """
    if state["current_task"] is None and len(state["work_list"]) >= 2:
        left = state["work_list"].pop(0)
        right = state["work_list"].pop(0)
        state["current_task"] = {
            "left": left,
            "right": right,
            "i": 0,
            "j": 0,
            "merged": []
        }
    return state


def complete_merge_task(state: dict) -> dict:
    """
    When one side of the current merge task is exhausted, append the remainder,
    push the merged result back into the work_list, and clear the current_task.
    If only one sublist remains in work_list, mark the session as complete.
    """
    task = state["current_task"]
    left = task["left"]
    right = task["right"]
    i = task["i"]
    j = task["j"]
    merged = task["merged"]

    # Append any remaining items from left or right.
    if i < len(left):
        merged.extend(left[i:])
    if j < len(right):
        merged.extend(right[j:])

    # Push the merged list to the end of the work_list.
    state["work_list"].append(merged)
    state["current_task"] = None

    # If there is only one sublist remaining, the sort is complete.
    if len(state["work_list"]) == 1:
        state["status"] = "completed"
    return state

# ---------------------
# API Endpoints
# ---------------------
@app.post("/api/sort/start")
def start_session(input_data: StartSessionInput):
    """
    Start a new merge sort session. The input list is stored as references to the items (item IDs) in the session state,
    and a "work_list" is created as a list of single-item lists containing these item IDs.
    """
    items = input_data.items
    if not items:
        raise HTTPException(status_code=400, detail="List cannot be empty.")

    # Initial state: each provided item (which should be an item record ID from the Items table) becomes a one-element sublist.
    state = {
        "item_refs": items,
        "work_list": [[item] for item in items],
        "current_task": None,
        "status": "in_progress"
    }
    # Create a new record in Airtable; Airtable will generate an ID for the session.
    record = sessions_table.create({"state": json.dumps(state)})
    session_id = record["id"]
    return {"session_id": session_id}


@app.get("/api/sort/{session_id}/next")
def get_next_comparison(session_id: str):
    """
    Returns the next pair of items to compare.
    If no current merge task exists, one is initiated (if possible).
    If one side of the merge is exhausted, completes the task and moves on.
    """
    state = get_session_state(session_id)
    if state["status"] == "completed":
        return {"message": "Sorting complete.", "sorted_list": state["work_list"][0]}

    # Ensure there is an active merge task.
    state = initiate_merge_task(state)
    if state["current_task"] is None:
        # If no merge task can be initiated, sorting must be complete.
        state["status"] = "completed"
        update_session_state(session_id, state)
        return {"message": "Sorting complete.", "sorted_list": state["work_list"][0]}

    task = state["current_task"]
    left, right = task["left"], task["right"]
    i, j = task["i"], task["j"]

    # If one side is exhausted, finish the merge.
    if i >= len(left) or j >= len(right):
        state = complete_merge_task(state)
        update_session_state(session_id, state)
        # Recursively call to get the next comparison.
        return get_next_comparison(session_id)

    update_session_state(session_id, state)
    return {"item_a": left[i], "item_b": right[j]}


@app.post("/api/sort/{session_id}/compare")
def post_comparison(session_id: str, input_data: CompareInput):
    """
    Submits the user's decision for the current comparison.
    The decision is applied to update the current merge task.
    """
    choice = input_data.choice.strip().upper()
    if choice not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Choice must be 'A' or 'B'.")

    state = get_session_state(session_id)
    if state["status"] == "completed":
        return {"message": "Sorting already complete.", "sorted_list": state["work_list"][0]}

    if state["current_task"] is None:
        # If no task is active, try to initiate one.
        state = initiate_merge_task(state)
        if state["current_task"] is None:
            raise HTTPException(status_code=400, detail="No merge task available.")
    task = state["current_task"]

    # Apply the user's choice.
    if choice == "A":
        task["merged"].append(task["left"][task["i"]])
        task["i"] += 1
    else:  # choice == "B"
        task["merged"].append(task["right"][task["j"]])
        task["j"] += 1

    # If one side is now exhausted, complete the merge.
    if task["i"] >= len(task["left"]) or task["j"] >= len(task["right"]):
        state = complete_merge_task(state)
    # (If not, the current task remains active.)
    update_session_state(session_id, state)
    return {"message": "Choice recorded.", "next": get_next_comparison(session_id)}


@app.get("/api/sort/{session_id}/result")
def get_result(session_id: str):
    """
    Returns the final sorted list if the session is complete.
    """
    state = get_session_state(session_id)
    if state["status"] != "completed":
        raise HTTPException(status_code=400, detail="Sorting is not complete yet.")
    return {"sorted_list": state["work_list"][0]}

@app.options("/api/sort/start")
async def options_start():
    return {} 