import { useState } from "react";

<<<<<<< HEAD
export default function App() {
  const [url, setUrl] = useState("");
=======
import ScannerTabs from "./components/ScannerTabs";
import ResultCard from "./components/ResultCard";
import {
  analyzeEmail,
  analyzeText,
  analyzeUrl,
} from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [subject, setSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
>>>>>>> 5a9a7e0f789cfc6e27ef0129d373bedccb4039fa
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

<<<<<<< HEAD
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
=======
  function changeTab(tab) {
    setActiveTab(tab);
    setResult(null);
    setError("");
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      if (activeTab === "url") {
        setResult(await analyzeUrl(url));
      } else if (activeTab === "text") {
        setResult(await analyzeText(text));
      } else {
        setResult(
          await analyzeEmail(subject, emailBody)
        );
      }
    } catch (requestError) {
      setError(requestError.message);
>>>>>>> 5a9a7e0f789cfc6e27ef0129d373bedccb4039fa
    } finally {
      setLoading(false);
    }
  }

  return (
<<<<<<< HEAD
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
=======
    <main className="app-shell">
      <header>
        <div className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 64 64">
            <path d="M32 5 54 14v15c0 14-9 25-22 30C19 54 10 43 10 29V14Z" />
            <path d="m22 32 7 7 14-16" />
          </svg>
        </div>
        <div>
          <p className="eyebrow">AI-powered threat scanner</p>
          <h1>Browse with confidence.</h1>
          <p>Check a URL, message, or email before you trust it.</p>
        </div>
      </header>

      <ScannerTabs
        activeTab={activeTab}
        onChange={changeTab}
      />

      <form onSubmit={submit}>
        {activeTab === "url" && (
          <label>
            Website URL
            <input
              type="text"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com"
              required
            />
          </label>
        )}

        {activeTab === "text" && (
          <label>
            Message
            <textarea
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste the message here"
              rows="7"
              required
            />
          </label>
        )}

        {activeTab === "email" && (
          <>
            <label>
              Subject
              <input
                type="text"
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
              />
            </label>

            <label>
              Email body
              <textarea
                value={emailBody}
                onChange={(event) => setEmailBody(event.target.value)}
                rows="8"
                required
              />
            </label>
          </>
        )}

        <button type="submit" disabled={loading}>
          {loading && <span className="spinner" aria-hidden="true" />}
          {loading ? "Analyzing..." : "Scan for threats"}
        </button>
      </form>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <ResultCard result={result} />
    </main>
  );
}
>>>>>>> 5a9a7e0f789cfc6e27ef0129d373bedccb4039fa
