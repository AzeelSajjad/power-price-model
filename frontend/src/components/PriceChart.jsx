import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export default function PriceChart({ data }) {
  if (!data || data.length === 0) return <p className="no-data">No price data</p>;

  const sorted = [...data]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .map((d) => ({
      ...d,
      time: new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

  return (
    <div className="chart-container">
      <h3>Price (LBMP $/MWhr)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={sorted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: '#aaa' }} />
          <YAxis tick={{ fontSize: 11, fill: '#aaa' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e1e2f', border: '1px solid #444' }}
            labelStyle={{ color: '#aaa' }}
          />
          <Line type="monotone" dataKey="lbmp" stroke="#6366f1" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
