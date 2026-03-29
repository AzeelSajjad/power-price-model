from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import prices, load, weather, forecast, zones

app = FastAPI(
    title="NYISO Power Price API",
    description="API for NYISO electricity prices, demand, weather, and price forecasting",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones.router)
app.include_router(prices.router)
app.include_router(load.router)
app.include_router(weather.router)
app.include_router(forecast.router)


@app.get("/health")
def health():
    return {"status": "ok"}
