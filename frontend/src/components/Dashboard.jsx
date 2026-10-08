import { useEffect, useState } from "react";

import { getDashboard } from "../services/api";

function formatDate(value) {
  return new Date(value).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Dashboard({ refreshKey }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    getDashboard()
      .then((response) => {
        setData(response);
        setError("");
      })
      .catch((requestError) => setError(requestError.message));
  }, [refreshKey, retryKey]);

  const cards = data ? [
    ["Total scans", data.summary.total],
    ["Phishing", data.summary.phishing],
    ["Legitimate", data.summary.legitimate],
    ["Average risk", `${data.summary.average_risk}%`],
  ] : [];

  return (
    <section className="dashboard" aria-labelledby="dashboard-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Security overview</p>
          <h2 id="dashboard-title">Scan dashboard</h2>
        </div>
        <span className={error ? "offline-status" : "live-status"}>
          {error ? "Database unavailable" : "Database connected"}
        </span>
      </div>

      {error ? (
        <div className="error" role="alert">
          <span>Dashboard unavailable. Start the backend and check your database settings.</span>
          <button className="retry-button" type="button" onClick={() => setRetryKey((value) => value + 1)}>Retry</button>
        </div>
      ) : !data ? (
        <p className="dashboard-state">Loading dashboard...</p>
      ) : <>
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
                    <td>{formatDate(scan.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        </div>
      </>}
    </section>
  );
}
