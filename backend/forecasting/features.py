import pandas as pd
import numpy as np
from ..db import engine


def load_prices(zone: str = None) -> pd.DataFrame:
    query = "SELECT * FROM prices ORDER BY timestamp"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["name"] == zone]
    return df


def load_demand(zone: str = None) -> pd.DataFrame:
    query = "SELECT * FROM load ORDER BY timestamp"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["name"] == zone]
    return df


def load_weather(zone: str = None) -> pd.DataFrame:
    query = "SELECT * FROM weather ORDER BY timestamp"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    if zone:
        df = df[df["zone"] == zone]
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based features from the timestamp column."""
    df = df.copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    return df


def add_lag_features(df: pd.DataFrame, column: str, lags: list[int]) -> pd.DataFrame:
    """Add lagged values of a column as features."""
    df = df.copy()
    for lag in lags:
        df[f"{column}_lag_{lag}"] = df[column].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, column: str, windows: list[int]) -> pd.DataFrame:
    """Add rolling mean and std as features."""
    df = df.copy()
    for w in windows:
        df[f"{column}_roll_mean_{w}"] = df[column].rolling(window=w).mean()
        df[f"{column}_roll_std_{w}"] = df[column].rolling(window=w).std()
    return df


def build_feature_matrix(zone: str) -> pd.DataFrame:
    """Build a complete feature matrix for a given NYISO zone.

    Merges price, load, and weather data. Adds time features,
    lag features, and rolling statistics.
    """
    prices = load_prices(zone)
    demand = load_demand(zone)
    weather = load_weather(zone)

    if prices.empty:
        raise ValueError(f"No price data found for zone {zone}")

    # Base dataframe: prices
    df = prices[["timestamp", "lbmp", "marg_cost_loss", "marg_cost_congestion"]].copy()

    # Merge demand on nearest timestamp
    if not demand.empty:
        demand_cols = demand[["timestamp", "load"]].copy()
        df = pd.merge_asof(
            df.sort_values("timestamp"),
            demand_cols.sort_values("timestamp"),
            on="timestamp",
            direction="nearest",
        )

    # Merge weather on nearest timestamp
    if not weather.empty:
        weather_cols = weather[["timestamp", "temperature", "wind_speed", "cloud_cover"]].copy()
        df = pd.merge_asof(
            df.sort_values("timestamp"),
            weather_cols.sort_values("timestamp"),
            on="timestamp",
            direction="nearest",
        )

    # Time features
    df = add_time_features(df)

    # Lag features on price
    df = add_lag_features(df, "lbmp", lags=[1, 2, 3, 6, 12])

    # Rolling stats on price
    df = add_rolling_features(df, "lbmp", windows=[3, 6, 12])

    # Drop rows with NaNs from lagging/rolling
    df = df.dropna().reset_index(drop=True)

    return df
