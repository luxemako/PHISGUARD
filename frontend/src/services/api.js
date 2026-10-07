const API_URL = "http://127.0.0.1:8000/api";

async function request(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      (Array.isArray(data.detail)
        ? data.detail.map((item) => item.msg).join(" ")
        : data.detail) || "Analysis failed. Please try again."
    );
  }

  return data;
}

export function analyzeUrl(url) {
  return request("/analyze/url", { url });
}

export function analyzeText(text) {
  return request("/analyze/text", { text });
}

export function analyzeEmail(subject, body) {
  return request("/analyze/email", {
    subject,
    body,
  });
}
