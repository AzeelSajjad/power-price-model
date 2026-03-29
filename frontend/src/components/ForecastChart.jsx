import { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Area, ComposedChart, Legend,
} from 'recharts';
import { fetchMeanReversionForecast, fetchXGBoostForecast } from '../api/client';

export default function ForecastChart({ zone }) {
  const [mrData, setMrData] = useState(null);
  const [xgbData, setXgbData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!zone) return;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchMeanReversionForecast(zone, 12).catch(() => null),
      fetchXGBoostForecast(zone).catch(() => null),
    ]).then(([mr, xgb]) => {
      setMrData(mr);
      setXgbData(xgb);
      setLoading(false);
    }).catch(() => {
      setError('Failed to load forecasts');
      setLoading(false);
    });
  }, [zone]);

  if (loading) return <p className="loading">Loading forecasts...</p>;
  if (error) return <p className="no-data">{error}</p>;

  return (
    <div className="forecast-section">
      <MeanReversionChart data={mrData} />
      <XGBoostChart data={xgbData} />
    </div>
  );
}

function MeanReversionChart({ data }) {
  if (!data) return <p className="no-data">No mean reversion data</p>;

  const chartData = data.forecast.map((f) => ({
    step: `t+${f.step}`,
    forecast: f.forecast,
    lower_95: f.lower_95,
    upper_95: f.upper_95,
    band: [f.lower_95, f.upper_95],
  }));

  // Prepend current price as step 0
  chartData.unshift({
    step: 'now',
    forecast: data.current_price,
    lower_95: data.current_price,
    upper_95: data.current_price,
    band: [data.current_price, data.current_price],
  });

  const params = data.parameters;

  return (
    <div className="chart-container">
      <h3>Mean Reversion Forecast</h3>
      <div className="forecast-params">
        <span>Mu: ${params.mu}/MWhr</span>
        <span>Theta: {params.theta}</span>
        <span>Half-life: {params.half_life} periods</span>
        <span>Current: ${data.current_price}/MWhr</span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="step" tick={{ fontSize: 11, fill: '#aaa' }} />
          <YAxis tick={{ fontSize: 11, fill: '#aaa' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e1e2f', border: '1px solid #444' }}
            labelStyle={{ color: '#aaa' }}
          />
          <Area
            type="monotone"
            dataKey="upper_95"
            stroke="none"
            fill="#6366f122"
          />
          <Area
            type="monotone"
            dataKey="lower_95"
            stroke="none"
            fill="#1e1e2f"
          />
          <Line type="monotone" dataKey="forecast" stroke="#6366f1" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="upper_95" stroke="#6366f166" strokeWidth={1} strokeDasharray="4 4" dot={false} name="95% Upper" />
          <Line type="monotone" dataKey="lower_95" stroke="#6366f166" strokeWidth={1} strokeDasharray="4 4" dot={false} name="95% Lower" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function XGBoostChart({ data }) {
  if (!data) return <p className="no-data">Not enough data for XGBoost model</p>;

  const chartData = data.fitted.map((f) => ({
    time: new Date(f.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    actual: f.actual,
    predicted: f.predicted,
  }));

  const metrics = data.metrics;
  const topFeatures = data.feature_importance.slice(0, 5);

  return (
    <div className="chart-container">
      <h3>XGBoost Fitted vs Actual</h3>
      <div className="forecast-params">
        <span>MAE: ${metrics.mae}/MWhr</span>
        <span>RMSE: ${metrics.rmse}/MWhr</span>
        <span>R2: {metrics.r2}</span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#aaa' }} />
          <YAxis tick={{ fontSize: 11, fill: '#aaa' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e1e2f', border: '1px solid #444' }}
            labelStyle={{ color: '#aaa' }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line type="monotone" dataKey="actual" stroke="#6366f1" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={2} dot={false} strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
      <div className="feature-importance">
        <h4>Top Features</h4>
        {topFeatures.map((f) => (
          <div key={f.feature} className="feature-bar">
            <span className="feature-name">{f.feature}</span>
            <div className="feature-bar-fill" style={{ width: `${f.importance * 100}%` }} />
            <span className="feature-val">{(f.importance * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
