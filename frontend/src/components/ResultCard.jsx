export default function ResultCard({ result }) {
  if (!result) return null;

  const warnings = result.warning_signs ?? [];

  return (
    <section className={`result-card ${result.risk_level ?? result.prediction}`} aria-live="polite">
      <p className="result-label">Analysis result</p>
      <h2>{result.prediction.toUpperCase()}</h2>
      <div className="risk-row">
        <span>Risk score</span>
        <strong>{result.risk_score}%</strong>
      </div>
      <progress value={result.risk_score} max="100" aria-label={`Risk score ${result.risk_score} percent`} />

      {result.detected_urls?.length > 0 && (
        <p>URLs detected: {result.detected_urls.length}</p>
      )}

      {warnings.length > 0 && (
        <div className="warning-list">
          <h3>Indicators</h3>
          <ul>
            {warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      )}
    </section>
  );
}
