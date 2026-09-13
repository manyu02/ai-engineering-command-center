import { useEffect, useState } from "react";
import { getProfile, saveProfile } from "../api/client";

function Dashboard({
  setActivePage,
  onProfileLoaded,
  onProfileSaved,
}) {
  const [profile, setProfile] = useState(null);
  const [showSetup, setShowSetup] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    role: "",
    specialization: "",
    target_companies: "",
    preparation_days: "30",
    current_knowledge: "",
  });

  useEffect(() => {
    getProfile()
      .then((data) => {
        setProfile(data);
        onProfileLoaded?.(data);

        setForm({
          role: data.role || "",
          specialization: data.specialization || "",
          target_companies: Array.isArray(data.target_companies)
            ? data.target_companies.join(", ")
            : "",
          preparation_days: String(data.preparation_days || 30),
          current_knowledge: Array.isArray(data.current_knowledge)
            ? data.current_knowledge.join(", ")
            : "",
        });
      })
      .catch(() => {
        setShowSetup(true);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSave = async (event) => {
    event.preventDefault();

    if (!form.role.trim()) {
      setError("Target role is required.");
      return;
    }

    if (!form.specialization.trim()) {
      setError("Specialization is required.");
      return;
    }

    const preparationDays = Number(form.preparation_days);

    if (!Number.isInteger(preparationDays) || preparationDays < 1) {
      setError("Preparation time must be at least 1 day.");
      return;
    }
    setSaving(true);
    setError("");

    try {
      const payload = {
        role: form.role.trim(),
        specialization: form.specialization.trim(),
        target_companies: form.target_companies
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        preparation_days: preparationDays,
        current_knowledge: form.current_knowledge
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      };

      const response = await saveProfile(payload);
      const savedProfile = response.profile || response;

      setProfile(savedProfile);
      onProfileSaved?.(savedProfile);

      setForm({
        role: savedProfile.role || "",
        specialization: savedProfile.specialization || "",
        target_companies: Array.isArray(savedProfile.target_companies)
          ? savedProfile.target_companies.join(", ")
          : "",
        preparation_days: String(savedProfile.preparation_days || 30),
        current_knowledge: Array.isArray(savedProfile.current_knowledge)
          ? savedProfile.current_knowledge.join(", ")
          : "",
      });

      setShowSetup(false);
    } catch (err) {
      setError(err.message || "Unable to save profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <section className="dashboard-page">
        <div className="content-panel">
          <span className="eyebrow">INITIALIZING</span>
          <h3>Loading your command center...</h3>
        </div>
      </section>
    );
  }

  if (showSetup || !profile?.role) {
    return (
      <section className="dashboard-page">
        <div className="hero-card">
          <div>
            <span className="eyebrow">PROFILE SETUP</span>
            <h2>Configure your AI engineering command center.</h2>
            <p>
              Define your target role, specialization, companies, preparation
              window, and current skills. The system will use this profile to
              personalize your career intelligence.
            </p>
          </div>

          <div className="hero-orbit">
            <div className="orbit-core">AI</div>
          </div>
        </div>

        <form className="content-panel profile-form" onSubmit={handleSave}>
          <div className="panel-header">
            <div>
              <span className="eyebrow">YOUR PROFILE</span>
              <h3>Career configuration</h3>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="profile-role">Target role</label>
              <input
                id="profile-role"
                name="role"
                value={form.role}
                onChange={handleChange}
                placeholder="e.g. AI Engineer"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="profile-specialization">
                Specialization
              </label>
              <input
                id="profile-specialization"
                name="specialization"
                value={form.specialization}
                onChange={handleChange}
                placeholder="e.g. Generative AI & Agentic AI"
                required
              />
            </div>

            <div className="form-field form-field-wide">
              <label htmlFor="profile-companies">
                Target companies
              </label>
              <input
                id="profile-companies"
                name="target_companies"
                value={form.target_companies}
                onChange={handleChange}
                placeholder="e.g. Google, Anthropic, Microsoft, OpenAI"
              />
              <span className="field-hint">
                Separate companies with commas.
              </span>
            </div>

            <div className="form-field">
              <label htmlFor="profile-days">
                Preparation time (days)
              </label>
              <input
                id="profile-days"
                name="preparation_days"
                type="number"
                min="1"
                value={form.preparation_days}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-field form-field-wide">
              <label htmlFor="profile-knowledge">
                Current knowledge
              </label>
              <input
                id="profile-knowledge"
                name="current_knowledge"
                value={form.current_knowledge}
                onChange={handleChange}
                placeholder="e.g. Python, LLMs, RAG, MCP, Agents"
              />
              <span className="field-hint">
                Separate skills with commas.
              </span>
            </div>
          </div>

          {error && <div className="error-state">{error}</div>}

          <button className="primary-button" type="submit" disabled={saving}>
            {saving ? "Saving profile..." : "Initialize Command Center"}
          </button>
        </form>
      </section>
    );
  }

  return (
    <section className="dashboard-page">
      <div className="hero-card">
        <div>
          <span className="eyebrow">AI ENGINEERING COMMAND CENTER</span>

          <h2>
            Your path to becoming{" "}
            <span className="accent-text">{profile.role}</span>.
          </h2>

          <p>
            Your command center connects career goals, market intelligence,
            learning priorities, projects, and interview preparation.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => setActivePage("market")}
            >
              Analyze Market
            </button>

            <button
              className="secondary-button"
              onClick={() => setActivePage("roadmap")}
            >
              View Roadmap
            </button>
          </div>
        </div>

        <div className="hero-orbit">
          <div className="orbit-core">AI</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="stat-card">
          <span className="card-label">TARGET ROLE</span>
          <strong>{profile.role}</strong>
          <span className="card-muted">{profile.specialization}</span>
        </div>

        <div className="stat-card">
          <span className="card-label">PREPARATION</span>
          <strong>{profile.preparation_days} days</strong>
          <span className="card-muted">Available preparation window</span>
        </div>

        <div className="stat-card">
          <span className="card-label">TARGET COMPANIES</span>
          <strong>{profile.target_companies?.length || 0}</strong>
          <span className="card-muted">
            {profile.target_companies?.join(" • ") || "None configured"}
          </span>
        </div>

        <div className="stat-card">
          <span className="card-label">CURRENT SKILLS</span>
          <strong>{profile.current_knowledge?.length || 0}</strong>
          <span className="card-muted">
            {profile.current_knowledge?.join(" • ") || "None configured"}
          </span>
        </div>
      </div>

      <div className="section-header">
        <div>
          <span className="eyebrow">WORKSPACE</span>
          <h3>Command Center Modules</h3>
        </div>

        <button
          className="secondary-button"
          onClick={() => setShowSetup(true)}
        >
          Edit Profile
        </button>
      </div>

      <div className="module-grid">
        <button
          className="module-card"
          onClick={() => setActivePage("market")}
        >
          <span className="module-icon">◈</span>
          <span className="module-title">Market Intelligence</span>
          <span className="module-description">
            Discover live roles, hiring signals, and skill demand.
          </span>
        </button>

        <button
          className="module-card"
          onClick={() => setActivePage("roadmap")}
        >
          <span className="module-icon">◎</span>
          <span className="module-title">Learning Roadmap</span>
          <span className="module-description">
            Build a role-specific learning and project progression.
          </span>
        </button>

        <button
          className="module-card"
          onClick={() => setActivePage("interview")}
        >
          <span className="module-icon">◇</span>
          <span className="module-title">Interview Lab</span>
          <span className="module-description">
            Generate questions and receive structured evaluations.
          </span>
        </button>
      </div>
    </section>
  );
}

export default Dashboard;