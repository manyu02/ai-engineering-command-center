import { useState } from "react";
import { generatePlan } from "../api/client";

function RoadmapPage({
  profile,
  roadmap,
  onRoadmapGenerated,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      const result = await generatePlan();
      onRoadmapGenerated(result);
    } catch (err) {
      setError(err.message || "Unable to generate roadmap.");
    } finally {
      setLoading(false);
    }
  };

  if (!profile) {
    return (
      <section className="roadmap-page">
        <div className="page-intro">
          <span className="eyebrow">ADAPTIVE LEARNING</span>
          <h2>Your path from current skills to target role.</h2>
          <p>
            Configure your profile before generating a personalized roadmap.
          </p>
        </div>

        <div className="empty-state">
          <div className="empty-state-icon">◎</div>
          <h4>Profile required</h4>
          <p>
            Set your target role, specialization, preparation period, and
            current knowledge from the Dashboard first.
          </p>
        </div>
      </section>
    );
  }

  const roadmapDays = roadmap?.roadmap || [];
  const priorityGaps = roadmap?.priority_gaps || [];
  const marketSignals = roadmap?.market_signals || [];

  return (
    <section className="roadmap-page">
      <div className="page-intro">
        <span className="eyebrow">ADAPTIVE LEARNING</span>

        <h2>
          Your path from current skills to{" "}
          <span className="accent-text">{profile.role}</span>.
        </h2>

        <p>
          Your roadmap is generated from your profile, current job-market
          requirements, and preparation window.
        </p>
      </div>

      <div className="roadmap-summary">
        <div className="overview-card">
          <span className="card-label">TARGET ROLE</span>
          <strong>{profile.role}</strong>
          <span className="card-muted">
            {profile.specialization}
          </span>
        </div>

        <div className="overview-card">
          <span className="card-label">PREPARATION</span>
          <strong>{profile.preparation_days} days</strong>
          <span className="card-muted">
            Planned learning window
          </span>
        </div>

        <div className="overview-card">
          <span className="card-label">ROADMAP STATUS</span>

          <strong>
            {roadmap ? "GENERATED" : "NOT GENERATED"}
          </strong>

          <span className="card-muted">
            {roadmap
              ? `${roadmapDays.length} learning days`
              : "Generate when you are ready"}
          </span>
        </div>
      </div>

      {!roadmap && (
        <div className="content-panel roadmap-generate-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">ROADMAP ENGINE</span>
              <h3>Generate your personalized roadmap</h3>
            </div>

            <span className="panel-badge">READY</span>
          </div>

          <p className="roadmap-generate-description">
            The engine will analyze current job-market requirements against
            your existing knowledge and build a preparation plan for the
            configured {profile.preparation_days}-day window.
          </p>

          {error && (
            <div className="error-state" role="alert">
              {error}
            </div>
          )}

          <button
            className="primary-button roadmap-generate-button"
            type="button"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner" />
                Generating roadmap...
              </>
            ) : (
              "Generate Roadmap"
            )}
          </button>

          {loading && (
            <span className="roadmap-loading-note">
              The first generation may take a few seconds while live market
              data is analyzed.
            </span>
          )}
        </div>
      )}

      {roadmap && (
        <>
          <div className="content-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">MARKET INTELLIGENCE</span>
                <h3>Priority gaps</h3>
              </div>

              <span className="panel-badge">
                {priorityGaps.length}
              </span>
            </div>

            {priorityGaps.length === 0 ? (
              <div className="empty-state">
                <h4>No major gaps identified</h4>
                <p>
                  Your current knowledge profile covers the detected market
                  requirements.
                </p>
              </div>
            ) : (
              <div className="roadmap-gap-grid">
                {priorityGaps.map((gap, index) => (
                  <div className="roadmap-gap-card" key={`${gap.skill}-${index}`}>
                    <div className="roadmap-gap-top">
                      <span className="step-label">
                        {gap.priority?.toUpperCase() || "PRIORITY"}
                      </span>

                      <span className="roadmap-gap-frequency">
                        {gap.reason?.match(/\d+\/\d+/)?.[0] || ""}
                      </span>
                    </div>

                    <h4>{gap.skill}</h4>

                    <p>{gap.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="content-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">MARKET SIGNALS</span>
                <h3>What the market is asking for</h3>
              </div>

              <span className="panel-badge">
                {roadmap.market_jobs_analyzed || 0} JOBS
              </span>
            </div>

            {marketSignals.length === 0 ? (
              <div className="empty-state">
                <p>No market signals available.</p>
              </div>
            ) : (
              <div className="roadmap-signal-list">
                {marketSignals.map((signal, index) => (
                  <div className="roadmap-signal" key={index}>
                    <span className="roadmap-signal-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <span>{signal}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="content-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">LEARNING PATH</span>
                <h3>Day-by-day roadmap</h3>
              </div>

              <span className="panel-badge">
                {roadmapDays.length} DAYS
              </span>
            </div>

            <div className="roadmap-placeholder">
              {roadmapDays.map((day, index) => (
                <div className="roadmap-line" key={day.day || index}>
                  <div
                    className={`roadmap-node ${
                      index === 0 ? "active" : ""
                    }`}
                  >
                    {String(day.day || index + 1).padStart(2, "0")}
                  </div>

                  <div className="roadmap-step">
                    <span className="step-label">
                      DAY {day.day || index + 1}
                    </span>

                    <h4>{day.topic}</h4>

                    <p className="roadmap-why">
                      {day.why}
                    </p>

                    {Array.isArray(day.learn) && day.learn.length > 0 && (
                      <div className="roadmap-learn">
                        <span>LEARN</span>

                        <ul>
                          {day.learn.map((item, learnIndex) => (
                            <li key={learnIndex}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="roadmap-generated-state">
            <span className="status-dot" />
            <span>
              Roadmap generated and saved. It will remain unchanged until
              your profile is updated and you generate a new roadmap.
            </span>
          </div>
        </>
      )}
    </section>
  );
}

export default RoadmapPage;