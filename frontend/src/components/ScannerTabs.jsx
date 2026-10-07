const tabs = [
  { id: "text", label: "Message" },
  { id: "email", label: "Email" },
  { id: "url", label: "URL" },
];

export default function ScannerTabs({
  activeTab,
  onChange,
}) {
  return (
    <nav className="scanner-tabs" aria-label="Scanner type">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={activeTab === tab.id ? "active" : ""}
          aria-pressed={activeTab === tab.id}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}