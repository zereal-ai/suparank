# Suparank

A web application for ranking items using a merge sort algorithm.

## Development Setup

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env.local` and fill in your environment variables:
```bash
cp .env.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

## Deployment to Vercel

1. Push your code to a GitHub repository

2. Connect your repository to Vercel:
   - Go to [Vercel](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository

3. Configure environment variables in Vercel:
   - Go to Project Settings > Environment Variables
   - Add the following variables for each environment (Production/Preview):
     ```
     # Production environment
     NEXT_PUBLIC_API_URL=https://api.your-domain.com  # Your production API URL
     AIRTABLE_API_KEY=your_airtable_api_key
     AIRTABLE_BASE_ID=your_airtable_base_id
     AIRTABLE_TABLE_ID=your_airtable_table_id

     # Preview environments (optional, for PR previews)
     NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com  # Your staging API URL
     AIRTABLE_API_KEY=your_staging_airtable_api_key
     AIRTABLE_BASE_ID=your_staging_base_id
     AIRTABLE_TABLE_ID=your_staging_table_id
     ```

4. Git Integration:
   - Production deployments are automatically triggered when pushing to the main branch
   - Preview deployments are created for each Pull Request
   - Development environment uses your local `.env.local` file

5. Environment Behavior:
   - Production (main branch): Uses production environment variables
   - Preview (Pull Requests): Uses preview environment variables
   - Development (local): Uses `.env.local` variables

6. Automatic Deployments:
   - Vercel automatically deploys your application
   - Each environment gets its own URL:
     - Production: `your-app.vercel.app`
     - Preview: `your-app-git-pr-XX-username.vercel.app`
     - Development: `localhost:3000`

## Project Structure

- `src/app/` - Next.js application code
  - `components/` - React components
  - `api.ts` - API client functions
  - `page.tsx` - Main application page
- `api/` - Backend API code
  - `index.py` - FastAPI application
  - `suparank.py` - Ranking logic

## Features

- Add items with title and description
- Compare items in pairs
- Keyboard navigation (left/right arrows)
- Visual feedback for selections
- Persistent rankings in Airtable
- Reset ranking session

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
