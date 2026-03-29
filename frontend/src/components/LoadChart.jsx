import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export default function LoadChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No load data</p>;

  const sorted = [...data]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map((d) => ({
      ...d,
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      load: Math.round(d.load),
    }));

  return (
    <div className="chart-container">
      <h3>Load / Demand (MW)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={sorted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#aaa' }} />
          <YAxis tick={{ fontSize: 11, fill: '#aaa' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e1e2f', border: '1px solid #444' }}
            labelStyle={{ color: '#aaa' }}
          />
          <Area type="monotone" dataKey="load" stroke="#10b981" fill="#10b98133" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
