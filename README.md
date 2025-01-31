# Suparank

A web application for ranking items using a merge sort algorithm and Airtable as the backend.

## Setup

### 1. Airtable Setup

1. Create a new Airtable base
2. Create a table named "Items" with the following fields:
   - Title (Single line text)
   - Description (Long text)
   - Score (Number)
3. Get your Airtable API key:
   - Go to your [Airtable account](https://airtable.com/account)
   - Under API section, generate a new API key if you don't have one
4. Get your Base ID:
   - Open your Airtable base
   - Click "Help" -> "API Documentation"
   - Your base ID will be in the URL: `airtable.com/[BASE_ID]/api/docs`

### 2. Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your Airtable credentials in `.env`:
   ```
   AIRTABLE_TOKEN=your_api_key_here
   AIRTABLE_BASE_ID=your_base_id_here
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### 3. Installation

1. Install Python dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

### 4. Development

1. Start the Python API server:
   ```bash
   npm run dev:api
   ```

2. In a new terminal, start the Next.js frontend:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. Add items to rank through the web interface
2. Compare items one by one
3. View the final rankings sorted by score

## License

MIT
