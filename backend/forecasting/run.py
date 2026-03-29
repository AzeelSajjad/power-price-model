"""Runner to train and generate forecasts for a given NYISO zone.

Usage:
    python -m backend.forecasting.run            # defaults to N.Y.C.
    python -m backend.forecasting.run --zone WEST
    python -m backend.forecasting.run --zone CAPITL --steps 12
"""

import argparse

from .features import build_feature_matrix, load_prices
from .mean_reversion import MeanReversionModel
from .ml_model import MLForecaster


def run(zone: str = "N.Y.C.", forecast_steps: int = 12):
    print(f"=== Forecasting for zone: {zone} ===\n")

    # ----- Load data -----
    prices = load_prices(zone)
    if prices.empty:
        print(f"No price data for zone {zone}. Run the data pipeline first.")
        return

    print(f"Price observations: {len(prices)}")
    print(f"Date range: {prices['timestamp'].min()} → {prices['timestamp'].max()}\n")

    # ----- Mean Reversion Model -----
    print("--- Mean Reversion (Ornstein-Uhlenbeck) ---")
    mr = MeanReversionModel()
    mr.fit(prices["lbmp"])
    print(mr.summary())

    current_price = prices["lbmp"].iloc[-1]
    mr_forecast = mr.forecast(current_price, steps=forecast_steps)
    print(f"Current price: ${current_price:.2f}/MWhr")
    print(f"Forecast ({forecast_steps} steps ahead):")
    print(mr_forecast.to_string(index=False))
    print()

    # ----- XGBoost Model -----
    print("--- XGBoost Model ---")
    try:
        df = build_feature_matrix(zone)
    except ValueError as e:
        print(f"Cannot build features: {e}")
        return

    if len(df) < 5:
        print(f"Only {len(df)} rows after feature engineering — need more data for ML model.")
        print("Keep the data pipeline running to accumulate more observations.")
        return

    ml = MLForecaster()
    ml.train(df)
    print(ml.summary())

    # Feature importances
    importance = ml.feature_importance()
    print("Top features:")
    print(importance.head(10).to_string(index=False))
    print()

    # Save model
    path = ml.save(zone)
    print(f"Model saved to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Power price forecasting")
    parser.add_argument("--zone", default="N.Y.C.", help="NYISO zone name")
    parser.add_argument("--steps", type=int, default=12, help="Forecast steps ahead")
    args = parser.parse_args()
    run(zone=args.zone, forecast_steps=args.steps)
