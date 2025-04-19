# Technical Context

## Technology Stack

### Frontend
- **Next.js**: React framework for server-rendered applications
- **React**: UI component library
- **TypeScript**: Strongly typed JavaScript
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Heroicons**: SVG icon set

### Backend
- **FastAPI**: Modern, fast Python web framework
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI
- **Pyairtable**: Python client for Airtable API
- **Python-dotenv**: Environment variable management

### Data Storage
- **Airtable**: Cloud-based spreadsheet database service
  - Items Table: Stores items to be ranked
  - Sessions Table: Stores sorting session state

### Deployment
- **Vercel**: Platform for frontend and serverless backend deployment
- **Environment Variables**: Configuration management for different environments

## Development Setup

### Prerequisites
1. Node.js (v14+)
2. Python (v3.8+)
3. Airtable account and API key

### Local Environment Setup
1. Clone repository
2. Create and activate Python virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install Python dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Install Node.js dependencies
   ```bash
   npm install
   ```
5. Create `.env` file from `.env.example`
   ```bash
   cp .env.example .env
   ```
6. Configure Airtable credentials in `.env`

### Running the Application
1. Start the Python API server
   ```bash
   npm run dev:api
   ```
2. Start the Next.js frontend (in a separate terminal)
   ```bash
   npm run dev
   ```
3. Access the application at http://localhost:3000

## Technical Constraints

### API URL Configuration
- Development: http://localhost:8000
- Production: Set in Vercel dashboard

### Airtable Requirements
- API Key: Required for authentication
- Base ID: Identifies the Airtable base
- Table ID: Identifies specific tables for items and sessions
- Table Structure:
  - Items Table: Requires 'title' and 'description' fields
  - Sessions Table: Requires 'state' field for JSON data

### Cross-Origin Resource Sharing (CORS)
- Backend is configured to allow all origins for development
- Production should implement appropriate CORS restrictions

### Environment Variables
- NEXT_PUBLIC_API_URL: API endpoint for frontend
- AIRTABLE_API_KEY: Authentication for Airtable
- AIRTABLE_BASE_ID: Identifies the Airtable base
- AIRTABLE_TABLE_ID: Identifies the Airtable table for items

## Deployment Process

### Vercel Setup
1. Connect GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Vercel automatically deploys the application

### Environment Management
- Production (main branch): Uses production environment variables
- Preview (Pull Requests): Uses preview environment variables
- Development (local): Uses `.env` variables 