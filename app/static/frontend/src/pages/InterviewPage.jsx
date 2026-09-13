import { useState } from "react";

function InterviewPage() {
  const [role, setRole] = useState("AI Engineer");
  const [specialization, setSpecialization] = useState("Generative AI");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [history, setHistory] = useState([]);
  const [evaluation, setEvaluation] = useState(null);
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [loadingEvaluation, setLoadingEvaluation] = useState(false);
  const [error, setError] = useState("");

  const generateQuestion = async () => {
    setLoadingQuestion(true);
    setError("");

    try {
      const response = await fetch("/api/v1/interview/question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role,
          specialization,
          history,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate question.");
      }

      setQuestion(data.question);
      setAnswer("");
      setEvaluation(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingQuestion(false);
    }
  };

  const handleEvaluate = async (event) => {
    event.preventDefault();

    if (!question || !answer.trim()) {
      setError("Generate a question and provide an answer first.");
      return;
    }

    setLoadingEvaluation(true);
    setError("");

    try {
      const response = await fetch("/api/v1/interview/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role,
          question,
          answer,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to evaluate answer.");
      }

      setEvaluation(data);

      setHistory((currentHistory) => [
        ...currentHistory,
        {
          question,
          answer,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingEvaluation(false);
    }
  };

  const adaptive = evaluation?.adaptive_learning;

  return (
    <section className="interview-page">
      <div className="page-intro">
        <span className="eyebrow">INTERVIEW INTELLIGENCE</span>
        <h2>Practice like the interview is already happening.</h2>
        <p>
          Generate role-specific questions, submit your answers, and use
          structured evaluation to identify where you need to improve.
        </p>
      </div>

      <div className="content-panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">INTERVIEW SETUP</span>
            <h3>Choose your target</h3>
          </div>
          <span className="panel-badge">AI</span>
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="interview-role">Target role</label>
            <input
              id="interview-role"
              value={role}
              onChange={(event) => setRole(event.target.value)}
              placeholder="e.g. AI Engineer"
            />
          </div>

          <div className="form-field">
            <label htmlFor="interview-specialization">
              Specialization
            </label>
            <input
              id="interview-specialization"
              value={specialization}
              onChange={(event) => setSpecialization(event.target.value)}
              placeholder="e.g. Generative AI"
            />
          </div>
        </div>
      </div>

      <div className="interview-grid">
        <div className="content-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">QUESTION</span>
              <h3>Interview prompt</h3>
            </div>
            <span className="panel-badge">AI</span>
          </div>

          <div className="question-box">
            <span>Question</span>
            <p>
              {question ||
                "Your generated interview question will appear here once the interview session begins."}
            </p>
          </div>

          <button
            className="primary-button"
            type="button"
            onClick={generateQuestion}
            disabled={loadingQuestion}
          >
            {loadingQuestion ? "Generating..." : "Generate Question"}
          </button>
        </div>

        <div className="content-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">EVALUATION</span>
              <h3>Answer analysis</h3>
            </div>
            <span className="panel-badge">AI</span>
          </div>

          <form onSubmit={handleEvaluate}>
            <div className="form-field">
              <label htmlFor="interview-answer">Your answer</label>

              <textarea
                id="interview-answer"
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Write your interview answer here..."
                rows="10"
              />
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={loadingEvaluation || !question}
            >
              {loadingEvaluation ? "Evaluating..." : "Evaluate Answer"}
            </button>
          </form>
        </div>
      </div>

      {error && (
        <div className="content-panel">
          <div className="error-state">{error}</div>
        </div>
      )}

      <div className="evaluation-grid">
        <div className="overview-card">
          <span className="card-label">TECHNICAL DEPTH</span>

          <strong>
            {evaluation?.score !== undefined
              ? `${evaluation.score}/10`
              : "—"}
          </strong>

          <span className="card-muted">
            {evaluation
              ? evaluation.missing_concepts?.length
                ? `${evaluation.missing_concepts.length} concepts to improve`
                : "Strong concept coverage"
              : "Awaiting evaluation"}
          </span>
        </div>

        <div className="overview-card">
          <span className="card-label">COMMUNICATION</span>

          <strong>{evaluation ? "AI" : "—"}</strong>

          <span className="card-muted">
            {evaluation
              ? evaluation.improvements?.length
                ? `${evaluation.improvements.length} improvement areas`
                : "Clear response structure"
              : "Awaiting evaluation"}
          </span>
        </div>

        <div className="overview-card">
          <span className="card-label">OVERALL SCORE</span>

          <strong>
            {evaluation?.score !== undefined
              ? `${evaluation.score}/10`
              : "—"}
          </strong>

          <span className="card-muted">
            {evaluation
              ? "Latest answer evaluated"
              : "No answer evaluated"}
          </span>
        </div>
      </div>

      {evaluation && (
        <div className="content-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">FEEDBACK</span>
              <h3>What to improve</h3>
            </div>
            <span className="panel-badge">AI</span>
          </div>

          {evaluation.strengths?.length > 0 && (
            <div className="feedback-section">
              <strong>Strengths</strong>

              <ul>
                {evaluation.strengths.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {evaluation.missing_concepts?.length > 0 && (
            <div className="feedback-section">
              <strong>Missing concepts</strong>

              <ul>
                {evaluation.missing_concepts.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {evaluation.improvements?.length > 0 && (
            <div className="feedback-section">
              <strong>Improvements</strong>

              <ul>
                {evaluation.improvements.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {evaluation.ideal_answer_direction && (
            <div className="feedback-section">
              <strong>Ideal answer direction</strong>
              <p>{evaluation.ideal_answer_direction}</p>
            </div>
          )}
        </div>
      )}

      {adaptive && (
        <div className="content-panel adaptive-learning-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">ADAPTIVE LEARNING</span>
              <h3>Your next move</h3>
            </div>

            <span className="panel-badge">
              {adaptive.priority?.toUpperCase() || "AI"}
            </span>
          </div>

          <div className="adaptive-grid">
            <div className="adaptive-card">
              <span className="card-label">PRIORITY</span>
              <strong>{adaptive.priority || "—"}</strong>
              <span className="card-muted">
                Based on your latest interview performance
              </span>
            </div>

            <div className="adaptive-card">
              <span className="card-label">FOCUS TOPICS</span>

              {adaptive.focus_topics?.length > 0 ? (
                <div className="topic-list">
                  {adaptive.focus_topics.map((topic, index) => (
                    <span className="topic-chip" key={index}>
                      {topic}
                    </span>
                  ))}
                </div>
              ) : (
                <span className="card-muted">
                  No major weak concepts identified.
                </span>
              )}
            </div>
          </div>

          {adaptive.recommendation && (
            <div className="adaptive-recommendation">
              <span className="card-label">RECOMMENDATION</span>
              <p>{adaptive.recommendation}</p>
            </div>
          )}

          {adaptive.practice_actions?.length > 0 && (
            <div className="feedback-section">
              <strong>Practice actions</strong>

              <ul>
                {adaptive.practice_actions.map((action, index) => (
                  <li key={index}>{action}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default InterviewPage;