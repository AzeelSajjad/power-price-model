import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass
import joblib
from pathlib import Path


MODELS_DIR = Path(__file__).parent / "saved_models"
MODELS_DIR.mkdir(exist_ok=True)

TARGET = "lbmp"

# Features to exclude from training
EXCLUDE_COLS = ["timestamp", TARGET]


@dataclass
class ModelMetrics:
    mae: float
    rmse: float
    r2: float


class MLForecaster:
    """XGBoost-based power price forecaster.

    Uses time-series-aware cross-validation and feature scaling.
    """

    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            min_child_weight=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.feature_names: list[str] = []
        self.metrics: ModelMetrics | None = None

    def _get_feature_cols(self, df: pd.DataFrame) -> list[str]:
        return [c for c in df.columns if c not in EXCLUDE_COLS]

    def train(self, df: pd.DataFrame) -> ModelMetrics:
        """Train the model on a feature matrix.

        Args:
            df: Feature matrix from build_feature_matrix().
                Must contain a 'lbmp' target column.
        """
        self.feature_names = self._get_feature_cols(df)
        X = df[self.feature_names].values
        y = df[TARGET].values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # Evaluate with time-series CV
        self.metrics = self._evaluate(df)
        return self.metrics

    def _evaluate(self, df: pd.DataFrame) -> ModelMetrics:
        """Evaluate using TimeSeriesSplit cross-validation."""
        X = df[self.feature_names].values
        y = df[TARGET].values

        n_splits = min(3, len(df) // 5)
        if n_splits < 2:
            # Not enough data for CV, report in-sample metrics
            preds = self.model.predict(self.scaler.transform(X))
            return ModelMetrics(
                mae=mean_absolute_error(y, preds),
                rmse=np.sqrt(mean_squared_error(y, preds)),
                r2=r2_score(y, preds),
            )

        tscv = TimeSeriesSplit(n_splits=n_splits)
        all_y, all_preds = [], []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            model_clone = XGBRegressor(**self.model.get_params())
            model_clone.fit(X_train_s, y_train)

            preds = model_clone.predict(X_test_s)
            all_y.extend(y_test)
            all_preds.extend(preds)

        all_y = np.array(all_y)
        all_preds = np.array(all_preds)

        return ModelMetrics(
            mae=mean_absolute_error(all_y, all_preds),
            rmse=np.sqrt(mean_squared_error(all_y, all_preds)),
            r2=r2_score(all_y, all_preds),
        )

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Generate predictions for new data."""
        X = df[self.feature_names].values
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def feature_importance(self) -> pd.DataFrame:
        """Return feature importances sorted by importance."""
        importances = self.model.feature_importances_
        return (
            pd.DataFrame({"feature": self.feature_names, "importance": importances})
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )

    def save(self, zone: str) -> Path:
        """Save model and scaler to disk."""
        path = MODELS_DIR / f"xgboost_{zone}.joblib"
        joblib.dump({"model": self.model, "scaler": self.scaler, "features": self.feature_names}, path)
        return path

    def load(self, zone: str) -> None:
        """Load a previously saved model."""
        path = MODELS_DIR / f"xgboost_{zone}.joblib"
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.feature_names = data["features"]

    def summary(self) -> str:
        if self.metrics is None:
            return "Model not trained."
        m = self.metrics
        return (
            f"XGBoost Model Metrics:\n"
            f"  MAE:  ${m.mae:.2f}/MWhr\n"
            f"  RMSE: ${m.rmse:.2f}/MWhr\n"
            f"  R²:    {m.r2:.4f}\n"
        )
