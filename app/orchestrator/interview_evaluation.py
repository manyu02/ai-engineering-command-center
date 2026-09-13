import json

from app.orchestrator.adaptive_learning import AdaptiveLearning


class InterviewEvaluator:

    def __init__(self, llm):
        self.llm = llm
        self.adaptive_learning = AdaptiveLearning()

    async def evaluate(self, role, question, answer):
        prompt = f"""
You are an AI engineering interview evaluator.

ROLE:
{role}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Evaluate the answer fairly.

Return ONLY valid JSON:
{{
  "score": 0,
  "strengths": [],
  "missing_concepts": [],
  "improvements": [],
  "ideal_answer_direction": ""
}}

Rules:
- Score from 0 to 10.
- Do not invent facts about the candidate.
- Evaluate only the supplied answer.
- Keep the feedback practical.
"""

        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        evaluation = json.loads(content)

        evaluation["adaptive_learning"] = (
            self.adaptive_learning.generate_adjustments(
                evaluation
            )
        )

        return evaluation