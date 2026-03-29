import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class MeanReversionParams:
    """Parameters for the Ornstein-Uhlenbeck mean reversion model.

    dP = theta * (mu - P) * dt + sigma * dW

    theta: speed of mean reversion (higher = faster reversion)
    mu: long-run equilibrium price
    sigma: volatility of the process
    """
    theta: float
    mu: float
    sigma: float
    half_life: float


class MeanReversionModel:
    """Ornstein-Uhlenbeck mean reversion model for power prices.

    Estimates parameters from historical price data using OLS on the
    discretized form: P(t) - P(t-1) = theta * (mu - P(t-1)) * dt + noise
    """

    def __init__(self):
        self.params: MeanReversionParams | None = None

    def fit(self, prices: pd.Series, dt: float = 1.0) -> MeanReversionParams:
        """Fit the OU model to a time series of prices.

        Args:
            prices: Series of price observations (chronologically ordered).
            dt: Time step between observations (default 1.0, meaning
                parameters are in units of the observation interval).
        """
        prices = prices.dropna().values
        if len(prices) < 3:
            raise ValueError("Need at least 3 price observations to fit")

        dp = np.diff(prices)
        p_prev = prices[:-1]

        # OLS regression: dp = a + b * p_prev
        # where b = -theta*dt, a = theta*mu*dt
        X = np.column_stack([np.ones(len(p_prev)), p_prev])
        beta = np.linalg.lstsq(X, dp, rcond=None)[0]

        a, b = beta[0], beta[1]

        theta = -b / dt
        if theta <= 0:
            # If no mean reversion detected, use a weak default
            theta = 0.01

        mu = a / (theta * dt)
        residuals = dp - (a + b * p_prev)
        sigma = np.std(residuals) / np.sqrt(dt)
        half_life = np.log(2) / theta if theta > 0 else np.inf

        self.params = MeanReversionParams(
            theta=theta, mu=mu, sigma=sigma, half_life=half_life
        )
        return self.params

    def forecast(self, current_price: float, steps: int, dt: float = 1.0) -> pd.DataFrame:
        """Generate point forecasts and confidence bands.

        Args:
            current_price: The most recent observed price.
            steps: Number of steps ahead to forecast.
            dt: Time step between observations.

        Returns:
            DataFrame with columns: step, forecast, lower_95, upper_95
        """
        if self.params is None:
            raise RuntimeError("Model not fitted. Call fit() first.")

        theta = self.params.theta
        mu = self.params.mu
        sigma = self.params.sigma

        forecasts = []
        for i in range(1, steps + 1):
            t = i * dt
            # E[P(t)] = mu + (P0 - mu) * exp(-theta * t)
            expected = mu + (current_price - mu) * np.exp(-theta * t)

            # Var[P(t)] = (sigma^2 / (2*theta)) * (1 - exp(-2*theta*t))
            if theta > 0:
                variance = (sigma**2 / (2 * theta)) * (1 - np.exp(-2 * theta * t))
            else:
                variance = sigma**2 * t

            std = np.sqrt(max(variance, 0))

            forecasts.append({
                "step": i,
                "forecast": expected,
                "lower_95": expected - 1.96 * std,
                "upper_95": expected + 1.96 * std,
            })

        return pd.DataFrame(forecasts)

    def summary(self) -> str:
        if self.params is None:
            return "Model not fitted."
        p = self.params
        return (
            f"Mean Reversion (Ornstein-Uhlenbeck) Parameters:\n"
            f"  Long-run mean (mu):      ${p.mu:.2f}/MWhr\n"
            f"  Reversion speed (theta):  {p.theta:.4f}\n"
            f"  Volatility (sigma):       {p.sigma:.4f}\n"
            f"  Half-life:                {p.half_life:.1f} periods\n"
        )
