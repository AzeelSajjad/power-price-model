from fastapi import APIRouter
import pandas as pd
from ...db import engine

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("/")
def list_zones():
    """List all available NYISO zones."""
    df = pd.read_sql("SELECT DISTINCT name FROM prices ORDER BY name", engine)
    return {"zones": df["name"].tolist()}
