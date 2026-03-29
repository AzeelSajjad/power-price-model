export default function StatsCards({ stats }) {
  if (!stats || stats.error) return null;

  const cards = [
    { label: 'Mean Price', value: `$${stats.mean_lbmp}/MWhr` },
    { label: 'Min Price', value: `$${stats.min_lbmp}/MWhr` },
    { label: 'Max Price', value: `$${stats.max_lbmp}/MWhr` },
    { label: 'Std Dev', value: `$${stats.std_lbmp}/MWhr` },
    { label: 'Observations', value: stats.count },
  ];

  return (
    <div className="stats-cards">
      {cards.map((c) => (
        <div key={c.label} className="stat-card">
          <span className="stat-label">{c.label}</span>
          <span className="stat-value">{c.value}</span>
        </div>
      ))}
    </div>
  );
}
