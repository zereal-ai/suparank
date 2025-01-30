from pyairtable import Api
import os
from dotenv import load_dotenv


def create_example_tasks(table):
    example_tasks = [
        {
            "Title": "Write Project Documentation",
            "Description": "Create comprehensive documentation for the current project, including setup instructions and API reference.",
            "Score": 0,
        },
        {
            "Title": "Fix Navigation Bug",
            "Description": "Investigate and fix the navigation menu that's not working correctly on mobile devices.",
            "Score": 0,
        },
        {
            "Title": "Implement Dark Mode",
            "Description": "Add dark mode support to the application, including user preference persistence.",
            "Score": 0,
        },
        {
            "Title": "Write Unit Tests",
            "Description": "Increase test coverage by writing unit tests for the recently added features.",
            "Score": 0,
        },
        {
            "Title": "Setup CI/CD Pipeline",
            "Description": "Configure GitHub Actions for automated testing and deployment.",
            "Score": 0,
        },
    ]

    print("\nCreating example tasks...")
    for task in example_tasks:
        try:
            record = table.create(task)
            print(f"Created task: {task['Title']}")
        except Exception as e:
            print(f"Error creating task '{task['Title']}': {e}")


def setup_airtable():
    load_dotenv()

    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_id = "tblDb3jQiPGFeDU9e"

    if not token or not base_id:
        print(
            "Error: Please ensure AIRTABLE_TOKEN and AIRTABLE_BASE_ID are set in .env"
        )
        return

    api = Api(token)
    table = api.table(base_id, table_id)

    try:
        records = table.all()
        print("\nConnection successful! Found", len(records), "records")
    except Exception as e:
        print(f"Error connecting to table: {e}")
        return

    # Get current schema
    schema = table.schema()
    print("\nCurrent fields:")
    existing_fields = {field.name for field in schema.fields}
    for field in schema.fields:
        print(f"- {field.name} ({field.id})")

    # Create our required fields if they don't exist
    print("\nChecking and creating required fields...")
    required_fields = [
        ("Title", "singleLineText"),
        ("Description", "multilineText"),
        ("Score", "number", {"precision": 1}),
    ]

    for field_info in required_fields:
        try:
            if len(field_info) == 3:
                name, field_type, options = field_info
                if name not in existing_fields:
                    table.create_field(name, field_type=field_type, options=options)
                    print(f"Created field: {name}")
                else:
                    print(f"Field already exists: {name}")
            else:
                name, field_type = field_info
                if name not in existing_fields:
                    table.create_field(name, field_type=field_type)
                    print(f"Created field: {name}")
                else:
                    print(f"Field already exists: {name}")
        except Exception as e:
            print(f"Error creating field {name}: {e}")

    # Create example tasks if table is empty
    records = table.all()
    if len(records) == 0:
        create_example_tasks(table)

    print("\nSetup complete! Verifying final schema...")
    schema = table.schema()
    print("\nFinal fields:")
    for field in schema.fields:
        print(f"- {field.name} ({field.id})")


if __name__ == "__main__":
    setup_airtable()
