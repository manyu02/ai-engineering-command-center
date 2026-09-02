import json

from langchain_ollama import ChatOllama


class RoadmapGenerator:

    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2:1b",
            temperature=0,
        )

    async def generate(
        self,
        role: str,
        specialization: str | None,
        preparation_days: int,
        current_knowledge: list[str],
        skill_gap: dict,
    ):

        prompt = f"""
Create a practical preparation roadmap for this candidate.

ROLE:
{role}

SPECIALIZATION:
{specialization or "Not specified"}

PREPARATION DAYS:
{preparation_days}

CURRENT KNOWLEDGE:
{json.dumps(current_knowledge, ensure_ascii=False)}

SKILL GAP:
{json.dumps(skill_gap, ensure_ascii=False)}

Return ONLY valid JSON using this structure:

{{
  "strategy": "",
  "weeks": [
    {{
      "week": 1,
      "focus": "",
      "topics": [],
      "deliverables": []
    }}
  ]
}}

Rules:
- Fit the roadmap within the available preparation time.
- Prioritize the highest-value skill gaps first.
- Do not recommend skills that are absent from the supplied skill-gap analysis.
- Build progressively from existing knowledge.
- Include practical deliverables, not only theory.
- Keep the response concise.
"""

        response = await self.llm.ainvoke(prompt)

        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        return json.loads(content)