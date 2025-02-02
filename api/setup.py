from pyairtable import Api
import os
from dotenv import load_dotenv
import json
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

# Define table schemas for only the required tables: Items and Sessions

tables = [
    {
        # Items table to store the actual items
        "fields": [
            {
                "description": "Title of the item",
                "name": "title",
                "type": "singleLineText"
            },
            {
                "description": "Description of the item",
                "name": "description",
                "type": "multilineText"
            }
        ],
        "description": "Actual items used for merge sort sessions",
        "name": "Items"
    },
    {
        # Sessions table that stores the merge sort session state as JSON (contains references to items)
        "fields": [
            {
                "description": "Merge sort session state stored as JSON (stores references to item IDs)",
                "name": "state",
                "type": "multilineText"
            }
        ],
        "description": "Merge sort sessions",
        "name": "Sessions"
    }
]

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

for table_def in tables:
    table_name = table_def["name"]
    print(f"\nCreating table: {table_name}")
    if table_name in existing_tables:
        print(f"\n⚠️  Table '{table_name}' already exists!")
        print("\nTo ensure the correct schema, please:")
        print("1. Delete the existing table in Airtable")
        print("2. Run this script again")
        print("\nExpected schema:")
        pprint.pprint(table_def["fields"], indent=2, width=100)
        continue

    try:
        response = requests.post(
            f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
            headers=headers,
            json=table_def
        )
        response.raise_for_status()
        print(f"✅ Successfully created table: {table_name}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error creating table {table_name}: {e}")
        if response.status_code != 422:
            raise

print("\nVerifying setup...")
response = requests.get(
    f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
    headers=headers
)
response.raise_for_status()
table_ids = {t["name"]: t["id"] for t in response.json()["tables"]}

missing_tables = []
for table_def in tables:
    if table_def["name"] not in table_ids:
        missing_tables.append(table_def["name"])

if missing_tables:
    print("\n❌ Missing tables:", ", ".join(missing_tables))
    print("Please delete all tables and run the script again.")
    exit(1)

print("\n✨ Setup complete! The following tables have been created and verified:")
for name, tid in table_ids.items():
    print(f"  - {name}: {tid}")

print("\nNote:")
print(" - The 'Items' table will store your actual items (title and description).")
print(" - The 'Sessions' table will be used by the merge sort service to store session state (which now holds references to item IDs rather than storing the full item data).")
