import json

from langchain_ollama import ChatOllama

from app.orchestrator.models import SkillGapResult


class SkillGapAnalyzer:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2:1b",
            temperature=0,
        )

    async def analyze(
        self,
        current_knowledge: list[str],
        market_analysis: str,
    ) -> dict:
        prompt = f"""
You are a skill gap analysis engine.

CURRENT KNOWLEDGE:
{current_knowledge}

MARKET ANALYSIS:
{market_analysis}

Return ONLY valid JSON matching this exact structure:
{{
  "summary": "brief summary",
  "gaps": [
    {{
      "skill": "skill name",
      "current_level": "beginner/intermediate/advanced",
      "required_level": "beginner/intermediate/advanced",
      "gap": "brief explanation",
      "priority": "high/medium/low"
    }}
  ]
}}

Do not use markdown.
Do not invent facts about the job market.
"""

        response = await self.llm.ainvoke(prompt)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(content)
            result = SkillGapResult.model_validate(data)
            return result.model_dump()
        except Exception as exc:
            raise ValueError(f"Invalid skill gap output: {exc}") from exc
