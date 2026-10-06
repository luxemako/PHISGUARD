import { useState } from "react";

export default function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyze(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyze/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        const message = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg.replace("Value error, ", "")).join(" ")
          : data.detail;

        throw new Error(message || "Unable to analyze URL");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>PhishGuard</h1>
      <p>Check whether a URL may be a phishing link.</p>

      <form onSubmit={analyze}>
        <input
          type="text"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          placeholder="https://example.com"
          minLength={4}
          required
        />
        <button disabled={loading}>
          {loading ? "Checking..." : "Check URL"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className={result.prediction}>
          <h2>{result.prediction.toUpperCase()}</h2>
          <p>Risk score: {result.risk_score}%</p>

          {result.warning_signs.length > 0 && (
            <ul>
              {result.warning_signs.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}