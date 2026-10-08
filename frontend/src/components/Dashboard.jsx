import { useEffect, useState } from "react";

import { getDashboard } from "../services/api";


export default function Dashboard({ refreshKey }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then((response) => {
        setData(response);
        setError("");
      })
      .catch((requestError) => setError(requestError.message));
  }, [refreshKey]);

  if (error) return <p className="error" role="alert">{error}</p>;
  if (!data) return <p className="dashboard-state">Loading dashboard...</p>;

  const cards = [
    ["Total scans", data.summary.total],
    ["Phishing", data.summary.phishing],
    ["Legitimate", data.summary.legitimate],
    ["Average risk", `${data.summary.average_risk}%`],
  ];

  return (
    <section className="dashboard" aria-labelledby="dashboard-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Security overview</p>
          <h2 id="dashboard-title">Scan dashboard</h2>
        </div>
        <span className="live-status">Database connected</span>
      </div>

      <div className="metric-grid">
        {cards.map(([label, value]) => (
          <article className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>

      <div className="history-card">
        <h3>Recent scans</h3>
        {data.recent_scans.length === 0 ? (
          <p className="dashboard-state">No scans yet. Run your first scan.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Type</th><th>Input</th><th>Result</th><th>Risk</th><th>Date</th></tr>
              </thead>
              <tbody>
                {data.recent_scans.map((scan) => (
                  <tr key={scan.id}>
                    <td>{scan.scan_type}</td>
                    <td className="preview-cell">{scan.input_preview}</td>
                    <td><span className={`status-pill ${scan.prediction}`}>{scan.prediction}</span></td>
                    <td>{scan.risk_score}%</td>
                    <td>{new Date(scan.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
