from pyairtable import Api
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import requests
import pprint

# Load environment variables
load_dotenv()

# Get Airtable credentials
token = os.getenv("AIRTABLE_TOKEN")
base_id = os.getenv("AIRTABLE_BASE_ID")

if not token or not base_id:
    raise ValueError("AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in environment variables")

# Initialize API
api = Api(token)

print("Setting up tables...")

# Define table schemas
tables = [
    {
        "fields": [
            {
                "description": "Title of the item",
                "name": "Title",
                "type": "singleLineText"
            },
            {
                "description": "Description of the item",
                "name": "Description",
                "type": "multilineText"
            }
        ],
        "description": "Items to be ranked",
        "name": "Items"
    },
    {
        "fields": [
            {
                "description": "Reference to item being split",
                "name": "ItemID",
                "type": "singleLineText"
            },
            {
                "description": "Unique ID for this split",
                "name": "SplitID",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "Depth in recursion",
                "name": "SplitLevel",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "Which side of the split",
                "name": "Side",
                "options": {
                    "choices": [
                        {
                            "name": "left"
                        },
                        {
                            "name": "right"
                        }
                    ]
                },
                "type": "singleSelect"
            },
            {
                "description": "Which split this came from",
                "name": "ParentSplitID",
                "type": "number",
                "options": {
                    "precision": 0
                }
            }
        ],
        "description": "Tracks merge sort splits",
        "name": "Splits"
    },
    {
        "fields": [
            {
                "description": "Unique ID for this merge",
                "name": "MergeID",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "Which split this belongs to",
                "name": "SplitID",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "Level of the merge",
                "name": "SplitLevel",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "Position in merged result",
                "name": "Position",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "description": "ID of winning item",
                "name": "WinnerID",
                "type": "singleLineText"
            },
            {
                "description": "ID of losing item",
                "name": "LoserID",
                "type": "singleLineText"
            },
            {
                "description": "When comparison was made",
                "name": "CompareTime",
                "type": "dateTime",
                "options": {
                    "dateFormat": {
                        "name": "iso"
                    },
                    "timeFormat": {
                        "name": "24hour"
                    },
                    "timeZone": "client"
                }
            }
        ],
        "description": "Tracks merge sort comparisons and results",
        "name": "Merges"
    }
]

# Create tables
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get existing tables
response = requests.get(
    f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
    headers=headers
)
response.raise_for_status()
existing_tables = {t["name"]: t for t in response.json()["tables"]}

# Create new tables
for table in tables:
    table_name = table["name"]
    print(f"\nCreating table: {table_name}")
    
    if table_name in existing_tables:
        print(f"\n⚠️  Table '{table_name}' already exists!")
        print("\nTo ensure the correct schema, please:")
        print("1. Delete the existing table in Airtable")
        print("2. Run this script again")
        print("\nExpected schema:")
        pprint.pprint(table["fields"], indent=2, width=100)
        continue

    try:
        response = requests.post(
            f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
            headers=headers,
            json=table
        )
        response.raise_for_status()
        print(f"✅ Successfully created table: {table_name}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error creating table {table_name}: {e}")
        if response.status_code != 422:  # Only exit if it's not a schema/exists error
            raise

# Verify setup
print("\nVerifying setup...")

# Get final table IDs
response = requests.get(
    f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
    headers=headers
)
response.raise_for_status()
table_ids = {t["name"]: t["id"] for t in response.json()["tables"]}

# Check all tables exist
missing_tables = []
for table in tables:
    if table["name"] not in table_ids:
        missing_tables.append(table["name"])

if missing_tables:
    print("\n❌ Missing tables:", ", ".join(missing_tables))
    print("Please delete all tables and run the script again.")
    exit(1)

# Initialize Items table
items_table = api.table(base_id, table_ids["Items"])

print("\nLoading example entries...")

# Clear existing items
existing_records = items_table.all()
for record in existing_records:
    items_table.delete(record["id"])

# Add example items
example_file = Path(__file__).parent / "example_entries.json"
with example_file.open() as f:
    example_entries = json.load(f)

for entry in example_entries:
    items_table.create({
        "Title": entry["Title"],
        "Description": entry["Description"]
    })

# Verify items were loaded
loaded_items = items_table.all()
if len(loaded_items) == len(example_entries):
    print(f"✅ Successfully loaded {len(loaded_items)} items:")
    for item in loaded_items:
        print(f"  - {item['fields']['Title']}")
else:
    print("❌ Error: Not all items were loaded")
    exit(1)

print("\n✨ Setup complete! All tables created and example entries loaded.")
