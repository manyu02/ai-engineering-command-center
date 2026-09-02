import json

from langchain_ollama import ChatOllama

from app.orchestrator.models import RoadmapResult


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
    ) -> dict:
        prompt = f"""
You are a career roadmap generation engine.

ROLE:
{role}

SPECIALIZATION:
{specialization}

PREPARATION DAYS:
{preparation_days}

CURRENT KNOWLEDGE:
{current_knowledge}

SKILL GAP:
{skill_gap}

Create a practical preparation roadmap.

Return ONLY valid JSON matching this exact structure:
{{
  "strategy": "brief overall strategy",
  "weeks": [
    {{
      "week": 1,
      "focus": "main focus",
      "topics": ["topic 1", "topic 2"],
      "deliverables": ["deliverable 1", "deliverable 2"]
    }}
  ]
}}

Rules:
- Use only information supported by the supplied skill gap and profile.
- Do not invent job requirements.
- Keep the roadmap realistic for the available preparation time.
- Do not use markdown.
"""

        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(content)
            result = RoadmapResult.model_validate(data)
            return result.model_dump()
        except Exception as exc:
            raise ValueError(f"Invalid roadmap output: {exc}") from exc