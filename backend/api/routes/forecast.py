from fastapi import APIRouter, Query, HTTPException
from ...forecasting.features import load_prices, build_feature_matrix
from ...forecasting.mean_reversion import MeanReversionModel
from ...forecasting.ml_model import MLForecaster

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/mean-reversion/{zone}")
def forecast_mean_reversion(
    zone: str,
    steps: int = Query(12, ge=1, le=100, description="Number of steps to forecast"),
):
    """Forecast prices using the Ornstein-Uhlenbeck mean reversion model."""
    prices = load_prices(zone)
    if prices.empty:
        raise HTTPException(status_code=404, detail=f"No price data for zone {zone}")

    if len(prices) < 3:
        raise HTTPException(status_code=400, detail="Not enough data to fit model (need >= 3 observations)")

    model = MeanReversionModel()
    params = model.fit(prices["lbmp"])
    current_price = prices["lbmp"].iloc[-1]
    forecast_df = model.forecast(current_price, steps=steps)

    return {
        "zone": zone,
        "current_price": round(current_price, 2),
        "parameters": {
            "mu": round(params.mu, 2),
            "theta": round(params.theta, 4),
            "sigma": round(params.sigma, 4),
            "half_life": round(params.half_life, 1),
        },
        "forecast": forecast_df.round(2).to_dict(orient="records"),
    }


@router.get("/xgboost/{zone}")
def forecast_xgboost(zone: str):
    """Train XGBoost model and return metrics, predictions, and feature importances."""
    try:
        df = build_feature_matrix(zone)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if len(df) < 5:
        raise HTTPException(
            status_code=400,
            detail=f"Only {len(df)} rows after feature engineering — need more data",
        )

    model = MLForecaster()
    metrics = model.train(df)
    importance = model.feature_importance()

    predictions = [float(p) for p in model.predict(df)]
    actuals = [float(a) for a in df["lbmp"]]
    timestamps = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S").tolist()

    imp = importance.head(10)
    imp["importance"] = imp["importance"].astype(float)

    return {
        "zone": zone,
        "metrics": {
            "mae": round(float(metrics.mae), 2),
            "rmse": round(float(metrics.rmse), 2),
            "r2": round(float(metrics.r2), 4),
        },
        "feature_importance": imp.round(4).to_dict(orient="records"),
        "fitted": [
            {"timestamp": ts, "actual": round(a, 2), "predicted": round(p, 2)}
            for ts, a, p in zip(timestamps, actuals, predictions)
        ],
    }
