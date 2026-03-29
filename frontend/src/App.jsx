import { useState, useEffect } from 'react';
import ZoneSelector from './components/ZoneSelector';
import StatsCards from './components/StatsCards';
import PriceChart from './components/PriceChart';
import LoadChart from './components/LoadChart';
import WeatherChart from './components/WeatherChart';
import ForecastChart from './components/ForecastChart';
import {
  fetchZones, fetchPrices, fetchPriceStats, fetchLoad, fetchWeather,
} from './api/client';
import './App.css';

export default function App() {
  const [zones, setZones] = useState([]);
  const [zone, setZone] = useState('');
  const [prices, setPrices] = useState([]);
  const [stats, setStats] = useState(null);
  const [load, setLoad] = useState([]);
  const [weather, setWeather] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchZones().then((z) => {
      setZones(z);
      setZone(z.includes('N.Y.C.') ? 'N.Y.C.' : z[0]);
    });
  }, []);

  useEffect(() => {
    if (!zone) return;
    setLoading(true);

    Promise.all([
      fetchPrices(zone),
      fetchPriceStats(zone),
      fetchLoad(zone),
      fetchWeather(zone),
    ]).then(([p, s, l, w]) => {
      setPrices(p);
      setStats(s);
      setLoad(l);
      setWeather(w);
      setLoading(false);
    });
  }, [zone]);

  return (
    <div className="app">
      <header>
        <h1>NYISO Power Dashboard</h1>
        <p className="subtitle">Real-time electricity prices, demand, and forecasting</p>
        {zones.length > 0 && (
          <ZoneSelector zones={zones} selected={zone} onChange={setZone} />
        )}
      </header>

      {loading ? (
        <div className="loading">Loading data...</div>
      ) : (
        <main>
          <StatsCards stats={stats} />

          <div className="chart-grid">
            <PriceChart data={prices} />
            <LoadChart data={load} />
          </div>

          <div className="chart-grid single">
            <WeatherChart data={weather} />
          </div>

          <h2 className="section-title">Forecasting</h2>
          <ForecastChart zone={zone} />
        </main>
      )}
    </div>
  );
}
