from pyairtable import Api
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests


def load_example_entries():
    """Load example entries from JSON file"""
    json_path = Path(__file__).parent / "example_entries.json"
    with open(json_path, "r") as f:
        return json.load(f)


def setup_airtable():
    # Load environment variables
    load_dotenv()
    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_ID")

    if not token or not base_id:
        raise ValueError(
            "AIRTABLE_TOKEN and AIRTABLE_BASE_ID must be set in environment variables"
        )

    # Initialize Airtable API
    api = Api(token)

    # Define required fields
    required_fields = [
        {"name": "Title", "type": "singleLineText"},
        {"name": "Description", "type": "multilineText"},
        {"name": "Rank", "type": "number", "options": {"precision": 0}},
    ]

    try:
        # Get metadata about the base
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"https://api.airtable.com/v0/meta/bases/{base_id}/tables", headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get tables: {response.text}")

        tables = response.json().get("tables", [])
        existing_table = next((t for t in tables if t["name"] == "Entries"), None)

        if existing_table:
            print("\nFound existing table 'Entries'")
            table = api.table(base_id, existing_table["id"])

            # Check and create missing fields
            print("\nChecking fields...")
            existing_fields = {f["name"]: f for f in existing_table["fields"]}
            missing_fields = []
            for field in required_fields:
                if field["name"] not in existing_fields:
                    missing_fields.append(field)
                    print(f"- Missing field: {field['name']}")
                else:
                    print(f"- Found field: {field['name']}")

            # Create any missing fields
            if missing_fields:
                print("\nCreating missing fields...")
                for field in missing_fields:
                    print(f"- Creating field: {field['name']}")
                    response = requests.post(
                        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{existing_table['id']}/fields",
                        headers=headers,
                        json=field,
                    )
                    if response.status_code != 200:
                        raise Exception(
                            f"Failed to create field {field['name']}: {response.text}"
                        )
                    print(f"  ✓ Created field: {field['name']}")
            else:
                print("All required fields exist")

            # Check for existing entries
            existing_entries = table.all()
            if existing_entries:
                print(f"\nTable already contains {len(existing_entries)} entries")
                print("Skipping example entries")
                return existing_table["id"]
            else:
                print("\nTable exists but is empty")
        else:
            print("\nCreating new table 'Entries'...")
            # Create table using metadata API
            response = requests.post(
                f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
                headers=headers,
                json={
                    "name": "Entries",
                    "description": "Entries to be ranked",
                    "fields": required_fields,
                },
            )
            if response.status_code != 200:
                raise Exception(f"Failed to create table: {response.text}")

            table_data = response.json()
            table = api.table(base_id, table_data["id"])
            print("✓ Table created successfully")

        # Load and add example entries if table is empty
        print("\nAdding example entries to empty table...")
        example_entries = load_example_entries()
        records = table.batch_create(example_entries)
        for record in records:
            print(f"✓ Created: {record['fields']['Title']}")

        return table.id if existing_table else table_data["id"]

    except Exception as e:
        print(f"\nError in setup: {str(e)}")
        return None


if __name__ == "__main__":
    print("\nStarting Suparank setup...")
    table_id = setup_airtable()
    if table_id:
        print("\nSetup complete!")
        print("Add this to your .env file if not already present:")
        print(f"AIRTABLE_TABLE_ID={table_id}")
    else:
        print("\nSetup failed. Please check the errors above.")
