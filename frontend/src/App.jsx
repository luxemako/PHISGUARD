import { useState } from "react";

import ScannerTabs from "./components/ScannerTabs";
import ResultCard from "./components/ResultCard";
import Dashboard from "./components/Dashboard";
import {
  analyzeEmail,
  analyzeText,
  analyzeUrl,
} from "./services/api";

export default function App() {
  const [dashboardRefresh, setDashboardRefresh] = useState(0);
  const [activeTab, setActiveTab] = useState("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [subject, setSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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
      setDashboardRefresh((value) => value + 1);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell wide">
      <header className="hero">
        <div className="hero-copy">
          <div className="brand">
            <span className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 64 64">
                <path d="M32 5 54 14v15c0 14-9 25-22 30C19 54 10 43 10 29V14Z" />
                <path d="m22 32 7 7 14-16" />
              </svg>
            </span>
            <span>PhishGuard</span>
          </div>
          <p className="eyebrow">Smart phishing protection</p>
          <h1>Check first. Click safely.</h1>
          <p>A simple safety check for links, messages, and emails.</p>
        </div>
        <div className="security-graphic" role="img" aria-label="Animated shield blocking a phishing email">
          <svg viewBox="0 0 320 250">
            <circle className="orbit" cx="160" cy="125" r="94" />
            <circle className="orbit orbit-two" cx="160" cy="125" r="67" />
            <g className="shield-group">
              <path className="shield" d="M160 47 220 71v43c0 42-24 72-60 88-36-16-60-46-60-88V71Z" />
              <path className="check" d="m132 123 20 20 39-45" />
              <path className="scan-line" d="M112 106h96" />
            </g>
            <circle className="node node-one" cx="65" cy="104" r="8" />
            <circle className="node node-two" cx="253" cy="84" r="6" />
            <circle className="node node-three" cx="238" cy="181" r="7" />
            <path className="threat-trail" d="M18 132h74" />
            <g className="phish-mail">
              <rect x="24" y="117" width="42" height="30" rx="5" />
              <path d="m28 122 17 13 17-13" />
            </g>
            <g className="block-impact">
              <circle cx="102" cy="132" r="13" />
              <path d="m102 108v-10M102 166v-10M78 132H68M136 132h-10" />
            </g>
            <path className="phish-hook" d="M275 101v31c0 13-17 14-17 2 0-7 9-8 13-4" />
          </svg>
          <span className="motion-status"><i /> Threat blocked</span>
        </div>
      </header>

      <div className="workspace">
        <section className="scanner-panel" aria-labelledby="scanner-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Threat scanner</p>
              <h2 id="scanner-title">Scan for phishing</h2>
              <p className="section-copy">Choose a content type and paste what you want to check.</p>
            </div>
          </div>
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
              autoComplete="url"
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
              rows="4"
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
                placeholder="Paste the email content here"
                rows="4"
                required
              />
            </label>
          </>
        )}

        <button type="submit" disabled={loading}>
          {loading && <span className="spinner" aria-hidden="true" />}
          {!loading && (
            <svg className="button-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 3 20 6v5c0 5-3 8-8 10-5-2-8-5-8-10V6Z" />
              <path d="m9 12 2 2 4-5" />
            </svg>
          )}
          {loading ? "Analyzing..." : "Scan for threats"}
        </button>
      </form>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

          <ResultCard result={result} />
        </section>
        <Dashboard refreshKey={dashboardRefresh} />
      </div>
    </main>
  );
}
