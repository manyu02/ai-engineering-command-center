function Sidebar({ activePage, setActivePage }) {
  const navigation = [
    { id: "dashboard", label: "Dashboard", icon: "⌂" },
    { id: "market", label: "Market Intelligence", icon: "◈" },
    { id: "roadmap", label: "Learning Roadmap", icon: "◎" },
    { id: "interview", label: "Interview Lab", icon: "◇" },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">AI</div>
        <div>
          <div className="brand-title">Command Center</div>
          <div className="brand-subtitle">AI Engineering</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${
              activePage === item.id ? "active" : ""
            }`}
            onClick={() => setActivePage(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-dot" />
        <span>System Online</span>
      </div>
    </aside>
  );
}

export default Sidebar;
