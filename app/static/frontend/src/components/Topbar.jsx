const pageTitles = {
  dashboard: {
    title: "Command Center",
    subtitle: "Your AI engineering career intelligence hub",
  },
  market: {
    title: "Market Intelligence",
    subtitle: "Live signals from the AI engineering job market",
  },
  roadmap: {
    title: "Learning Roadmap",
    subtitle: "A personalized path from current skills to target roles",
  },
  interview: {
    title: "Interview Lab",
    subtitle: "Practice, evaluate, and improve your interview performance",
  },
};

function Topbar({ activePage }) {
  const page = pageTitles[activePage] || pageTitles.dashboard;

  return (
    <header className="topbar">
      <div>
        <h1>{page.title}</h1>
        <p>{page.subtitle}</p>
      </div>

      <div className="topbar-status">
        <span className="status-dot" />
        <span>AI Engine Online</span>
      </div>
    </header>
  );
}

export default Topbar;
