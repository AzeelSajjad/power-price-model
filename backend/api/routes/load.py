from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
from ...db import engine

router = APIRouter(prefix="/load", tags=["load"])


@router.get("/")
def get_load(
    zone: Optional[str] = Query(None, description="Filter by NYISO zone name"),
    limit: int = Query(100, ge=1, le=10000, description="Max rows to return"),
):
    """Get historical load/demand data, optionally filtered by zone."""
    query = "SELECT * FROM load ORDER BY timestamp DESC"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["name"] == zone]
    df = df.head(limit)
    return df.to_dict(orient="records")


@router.get("/latest")
def get_latest_load():
    """Get the most recent load reading for each zone."""
    query = """
        SELECT DISTINCT ON (name) *
        FROM load
        ORDER BY name, timestamp DESC
    """
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.to_dict(orient="records")
