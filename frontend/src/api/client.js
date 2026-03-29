import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

export const fetchZones = () => api.get('/zones/').then(r => r.data.zones);

export const fetchPrices = (zone, limit = 500) =>
  api.get('/prices/', { params: { zone, limit } }).then(r => r.data);

export const fetchLatestPrices = () =>
  api.get('/prices/latest').then(r => r.data);

export const fetchPriceStats = (zone) =>
  api.get('/prices/stats', { params: { zone } }).then(r => r.data);

export const fetchLoad = (zone, limit = 500) =>
  api.get('/load/', { params: { zone, limit } }).then(r => r.data);

export const fetchWeather = (zone) =>
  api.get('/weather/', { params: { zone, limit: 500 } }).then(r => r.data);

export const fetchLatestWeather = () =>
  api.get('/weather/latest').then(r => r.data);

export const fetchMeanReversionForecast = (zone, steps = 12) =>
  api.get(`/forecast/mean-reversion/${zone}`, { params: { steps } }).then(r => r.data);

export const fetchXGBoostForecast = (zone) =>
  api.get(`/forecast/xgboost/${zone}`).then(r => r.data);
