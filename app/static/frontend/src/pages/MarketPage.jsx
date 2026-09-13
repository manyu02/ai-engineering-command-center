import { useState } from "react";
import { analyzeMarket } from "../api/client";

function MarketPage() {
  const [role, setRole] = useState("");
  const [specialization, setSpecialization] = useState("");
  const [location, setLocation] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async (event) => {
    event.preventDefault();

    if (!role.trim()) {
      setError("Please enter a target role.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await analyzeMarket({
        role: role.trim(),
        specialization: specialization.trim() || null,
        location: location.trim() || null,
      });

      setData(result);
    } catch (err) {
      setError(err.message || "Unable to analyze the market.");
    } finally {
      setLoading(false);
    }
  };

  const jobs = data?.jobs || [];
  const jobsCount = jobs.length;

  return (
    <section className="market-page">
      <div className="page-intro">
        <span className="eyebrow">LIVE MARKET ANALYSIS</span>
        <h2>Understand what the market is asking for.</h2>
        <p>
          Search current AI engineering opportunities and identify the skills,
          technologies, and signals that matter for your target role.
        </p>
      </div>

      <form className="analysis-form" onSubmit={handleAnalyze}>
        <div className="form-field">
          <label htmlFor="market-role">Target role</label>
          <input
            id="market-role"
            value={role}
            onChange={(event) => setRole(event.target.value)}
            placeholder="e.g. AI Engineer"
            disabled={loading}
          />
        </div>

        <div className="form-field">
          <label htmlFor="market-specialization">Specialization</label>
          <input
            id="market-specialization"
            value={specialization}
            onChange={(event) => setSpecialization(event.target.value)}
            placeholder="e.g. LLM and Agentic AI"
            disabled={loading}
          />
        </div>

        <div className="form-field">
          <label htmlFor="market-location">Location</label>
          <input
            id="market-location"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="e.g. India or Remote"
            disabled={loading}
          />
        </div>

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? (
            <>
              <span className="loading-spinner" />
              Analyzing market...
            </>
          ) : (
            "Analyze Market"
          )}
        </button>
      </form>

      {error && (
        <div className="error-state" role="alert">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="market-overview">
            <div className="overview-card">
              <span className="card-label">LIVE JOBS</span>
              <strong>{jobsCount}</strong>
              <span className="card-muted">Jobs displayed</span>
            </div>

            <div className="overview-card">
              <span className="card-label">SPECIALIZATION</span>
              <strong>{data.specialization || "General"}</strong>
              <span className="card-muted">Target specialization</span>
            </div>

            <div className="overview-card">
              <span className="card-label">MARKET SIGNAL</span>
              <strong>LIVE</strong>
              <span className="card-muted">Current market data</span>
            </div>
          </div>

          <div className="content-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">MARKET ANALYSIS</span>
                <h3>Market intelligence</h3>
              </div>
              <span className="panel-badge">LIVE</span>
            </div>

            <div className="analysis-result">
              {data.analysis || "No market analysis returned."}
            </div>
          </div>

          <div className="content-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">JOB INTELLIGENCE</span>
                <h3>Matching opportunities</h3>
              </div>
              <span className="panel-badge">{jobsCount}</span>
            </div>

            <div className="job-list">
              {jobsCount === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon">◌</div>
                  <h4>No matching jobs found</h4>
                  <p>
                    Try a broader role, specialization, or location to
                    discover more opportunities.
                  </p>
                </div>
              ) : (
                jobs.map((item, index) => {
                  const job = item.job || item;

                  return (
                    <article
                      className="job-card"
                      key={job.job_id || job.url || index}
                    >
                      <div>
                        <span className="job-company">
                          {job.company || "Unknown company"}
                        </span>

                        <h4>{job.title || "Untitled role"}</h4>

                        <span className="job-location">
                          {job.location || "Location unavailable"}
                        </span>
                      </div>

                      {job.url && (
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="job-link"
                        >
                          View live job →
                        </a>
                      )}
                    </article>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </section>
  );
}

export default MarketPage;