from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
from ...db import engine

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/")
def get_weather(
    zone: Optional[str] = Query(None, description="Filter by NYISO zone name"),
    limit: int = Query(100, ge=1, le=10000, description="Max rows to return"),
):
    """Get historical weather data, optionally filtered by zone."""
    query = "SELECT * FROM weather ORDER BY timestamp DESC"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["zone"] == zone]
    df = df.head(limit)
    return df.to_dict(orient="records")


@router.get("/latest")
def get_latest_weather():
    """Get the most recent weather reading for each zone."""
    query = """
        SELECT DISTINCT ON (zone) *
        FROM weather
        ORDER BY zone, timestamp DESC
    """
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.to_dict(orient="records")
