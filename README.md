# Suparank

A command-line interface application that helps you prioritize tasks through pairwise comparisons. By comparing tasks two at a time, Suparank builds a ranked list of your tasks.

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set your Airtable credentials:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your Airtable token and base ID.

## Setup

Before first use, run the setup script to configure the Airtable schema and create example tasks:
```bash
python setup_airtable.py
```

## Usage

Run the application with sudo (required for keyboard input on macOS):
```bash
sudo python main.py
```

### Controls
- Left Arrow: Choose left task as more important
- Right Arrow: Choose right task as more important
- ESC: Exit application

## How it Works

1. Tasks are presented in pairs
2. For each pair, choose which task is more important
3. Each choice updates the ranking of both tasks
4. Continue until all tasks are ranked
5. Final ranking is displayed at the end

## Features

- Intuitive pairwise comparison interface
- Efficient ranking through merge sort approach
- Rich text UI with colorful panels
- Persistent storage in Airtable
- Keyboard controls
- Final ranked summary view

## Adding Tasks

Tasks can be added through Airtable directly, or by modifying the example tasks in `setup_airtable.py`.

## Requirements

- Python 3.6+
- Airtable account with API access
- Root privileges (for keyboard input on macOS)