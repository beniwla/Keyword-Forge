# Keyword Research Tool

A full-stack web application for keyword research and Google Ads campaign planning using FastAPI backend and React frontend.

## Features

- **Website Analysis**: Extract keywords from any website URL
- **Configuration-based Research**: Upload YAML config files for bulk keyword research
- **AI-Powered Ad Groups**: Automatically generate Google Ads campaign structures
- **Real-time Results**: Get keyword suggestions with search volumes and competition data

## Tech Stack

**Backend:**
- FastAPI
- OpenAI GPT API
- DataForSEO API
- Python 3.8+

**Frontend:**
- React/Vite
- Axios for API calls
- Modern responsive design

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- DataForSEO API credentials

### Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend Setup
cd frontend
npm install
npm run dev


### Environment Variables
Create `.env` files with your API credentials and auth for Third Party APIs

## Deployment
Deployed on Render.com with automatic GitHub integration.

## API Endpoints
- `POST /api/v1/keywords/search` - Analyze website keywords
- `POST /api/v1/keywords/search-from-config` - Config-based keyword research

## License
MIT License
