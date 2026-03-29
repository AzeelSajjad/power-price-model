import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

export default function WeatherChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No weather data</p>;

  const sorted = [...data]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map((d) => ({
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      temperature: Math.round(d.temperature * 10) / 10,
      wind_speed: Math.round(d.wind_speed * 10) / 10,
      cloud_cover: Math.round(d.cloud_cover),
    }));

  return (
    <div className="chart-container">
      <h3>Weather Conditions</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={sorted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#aaa' }} />
          <YAxis tick={{ fontSize: 11, fill: '#aaa' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e1e2f', border: '1px solid #444' }}
            labelStyle={{ color: '#aaa' }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="temperature" fill="#f59e0b" name="Temp (C)" />
          <Bar dataKey="wind_speed" fill="#3b82f6" name="Wind (km/h)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
