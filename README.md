# Restaurant Lead Finder AI

A powerful API to find, analyze, and score restaurant leads using Google Places and AI models.

## Architecture Overview
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (SQLAlchemy 2.0 Async + asyncpg)
- **APIs**: Google Places API, Google Vision API
- **AI Models**: Gemini & OpenAI (swappable via interface)

## Features
- Search restaurants by text query or location (latitude/longitude)
- Background async scanning to avoid blocking API
- Detailed restaurant data collection (address, phone, hours, rating)
- AI-driven lead scoring (premium score, collaboration score)
- Outreach message generation tailored to the restaurant

## Prerequisites
- Python 3.12+
- PostgreSQL
- Google Places API Key
- Google Vision API Key
- Gemini or OpenAI API Key

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment example and configure it:
   ```bash
   cp .env.example .env
   # Edit .env and fill in your API keys and database URL
   ```
5. Ensure PostgreSQL is running and create the database specified in your `DATABASE_URL`.

## Database Setup

Initialize and run database migrations using Alembic:

```bash
alembic init db/migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

## Running the Application

Run the FastAPI server with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the app is running, access the interactive API documentation at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root endpoint / Welcome message |
| GET | `/api/v1/health` | Health check endpoint |
| POST | `/api/v1/scan` | Trigger a text-based scan for restaurants |
| POST | `/api/v1/scan/location` | Trigger a location-based scan |
| GET | `/api/v1/restaurants` | List restaurants (pagination & filters) |
| GET | `/api/v1/restaurants/{id}` | Get specific restaurant details |
| PATCH | `/api/v1/restaurants/{id}` | Update a restaurant |
| DELETE | `/api/v1/restaurants/{id}` | Delete a restaurant |
| POST | `/api/v1/restaurants/analyze/{id}` | Re-run AI analysis on a restaurant |
| POST | `/api/v1/restaurants/outreach/{id}` | Generate outreach message |

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) |
| `GOOGLE_PLACES_API_KEY` | Key for Google Places API |
| `GOOGLE_VISION_API_KEY` | Key for Google Vision API |
| `GEMINI_API_KEY` | Key for Google Gemini API |
| `OPENAI_API_KEY` | Key for OpenAI API |
| `LLM_PROVIDER` | `gemini` or `openai` |
| `LOG_LEVEL` | Application logging level (`INFO`, `DEBUG`, etc.) |
| `LOG_FILE` | Path to log file |
| `API_KEY` | Optional key to secure endpoints |
| `SCAN_RADIUS_METERS` | Default radius for scans (e.g., 5000) |
| `MAX_RESULTS_PER_SCAN` | Limit results per scan (e.g., 20) |

## Testing

Run tests using pytest:

```bash
pytest
```

## License
MIT License
