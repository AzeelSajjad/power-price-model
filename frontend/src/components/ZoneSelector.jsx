export default function ZoneSelector({ zones, selected, onChange }) {
  return (
    <div className="zone-selector">
      <label htmlFor="zone-select">NYISO Zone</label>
      <select
        id="zone-select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
      >
        {zones.map((z) => (
          <option key={z} value={z}>{z}</option>
        ))}
      </select>
    </div>
  );
}
