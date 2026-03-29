from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
from ...db import engine

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/")
def get_prices(
    zone: Optional[str] = Query(None, description="Filter by NYISO zone name"),
    limit: int = Query(100, ge=1, le=10000, description="Max rows to return"),
):
    """Get historical price data, optionally filtered by zone."""
    query = "SELECT * FROM prices ORDER BY timestamp DESC"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["name"] == zone]
    df = df.head(limit)
    return df.to_dict(orient="records")


@router.get("/latest")
def get_latest_prices():
    """Get the most recent price for each zone."""
    query = """
        SELECT DISTINCT ON (name) *
        FROM prices
        ORDER BY name, timestamp DESC
    """
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    return df.to_dict(orient="records")


@router.get("/stats")
def get_price_stats(
    zone: Optional[str] = Query(None, description="Filter by NYISO zone name"),
):
    """Get summary statistics for prices."""
    query = "SELECT * FROM prices ORDER BY timestamp"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["name"] == zone]
    if df.empty:
        return {"error": "No data found"}

    stats = {
        "count": len(df),
        "mean_lbmp": round(df["lbmp"].mean(), 2),
        "min_lbmp": round(df["lbmp"].min(), 2),
        "max_lbmp": round(df["lbmp"].max(), 2),
        "std_lbmp": round(df["lbmp"].std(), 2),
        "earliest": str(df["timestamp"].min()),
        "latest": str(df["timestamp"].max()),
    }
    return stats
