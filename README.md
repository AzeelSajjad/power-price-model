# NYISO Power Price Model

A full-stack application for collecting, analyzing, and forecasting electricity prices from the New York Independent System Operator (NYISO). Includes automated data pipelines, ML-based price forecasting, and an interactive dashboard.

## Architecture

```
Data Sources                    Backend                         Frontend
NYISO CSV APIs  ──>  APScheduler pipelines  ──>  PostgreSQL  ──>  FastAPI  ──>  React Dashboard
Open-Meteo API  ──>  (prices, load, weather)                     (REST API)    (Recharts)
```

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, APScheduler, XGBoost, scikit-learn
**Frontend:** React, Vite, Recharts, Axios
**Database:** PostgreSQL 16 (Docker)
**Data Sources:** NYISO (prices & demand), Open-Meteo (weather)

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/AzeelSajjad/power-price-model.git
cd power-price-model
```

### 2. Create a `.env` file

```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=power-price-model
DATABASE_URL=postgresql+psycopg2://your_user:your_password@localhost:5432/power-price-model
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run database migrations

```bash
cd backend
alembic upgrade head
cd ..
```

### 6. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Running

You need three terminals:

**Terminal 1 — Data Pipelines** (fetches NYISO prices/load every 30s, weather every 15min):
```bash
source venv/bin/activate
python -m backend.data.nysio
```

**Terminal 2 — API Server:**
```bash
source venv/bin/activate
python -m uvicorn backend.api.app:app --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** to view the dashboard.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /zones/` | List all NYISO zones |
| `GET /prices/?zone=N.Y.C.` | Historical prices (optional zone filter) |
| `GET /prices/latest` | Most recent price per zone |
| `GET /prices/stats?zone=N.Y.C.` | Price summary statistics |
| `GET /load/?zone=N.Y.C.` | Historical load/demand data |
| `GET /load/latest` | Most recent load per zone |
| `GET /weather/?zone=N.Y.C.` | Historical weather data |
| `GET /weather/latest` | Most recent weather per zone |
| `GET /forecast/mean-reversion/{zone}?steps=12` | Ornstein-Uhlenbeck price forecast |
| `GET /forecast/xgboost/{zone}` | XGBoost model metrics and fitted values |

API docs available at **http://localhost:8000/docs** when the server is running.

## Forecasting Models

### Mean Reversion (Ornstein-Uhlenbeck)
Models price as a stochastic process that reverts to a long-run mean. Outputs point forecasts with 95% confidence bands. Well-suited for power markets where prices spike and revert.

### XGBoost
Gradient-boosted tree model trained on features including:
- Price lags and rolling statistics
- Load/demand data
- Weather (temperature, wind speed, cloud cover)
- Time features (hour, day of week, cyclical encoding)

Run forecasting from the CLI:
```bash
python -m backend.forecasting.run --zone "N.Y.C." --steps 12
```

## Project Structure

```
backend/
  api/             # FastAPI app and route handlers
  data/            # Data pipelines (NYISO, weather)
  forecasting/     # ML models (mean reversion, XGBoost)
  models/          # SQLAlchemy ORM models
  migrations/      # Alembic database migrations
  db.py            # Database connection
frontend/
  src/
    api/           # Axios API client
    components/    # React chart components
docker-compose.yml
requirements.txt
```
