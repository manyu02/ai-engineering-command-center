const API_BASE = "/api/v1";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Request failed.");
  }

  return data;
}

export async function getProfile() {
  return request("/profile");
}

export async function saveProfile(profile) {
  return request("/profile", {
    method: "POST",
    body: JSON.stringify(profile),
  });
}

export async function generatePlan() {
  return request("/plan/generate", {
    method: "POST",
  });
}

export async function analyzeMarket({ role, specialization, location }) {
  return request("/market/analyze", {
    method: "POST",
    body: JSON.stringify({
      role,
      specialization,
      location: location || null,
    }),
  });
}

export async function analyzeCommandCenter(payload) {
  return request("/command-center/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function generateInterviewQuestion(payload) {
  return request("/interview/question", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function evaluateInterviewAnswer(payload) {
  return request("/interview/evaluate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function adjustLearning(payload) {
  return request("/learning/adjust", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export default {
  getProfile,
  saveProfile,
  generatePlan,
  analyzeMarket,
  analyzeCommandCenter,
  generateInterviewQuestion,
  evaluateInterviewAnswer,
  adjustLearning,
};
