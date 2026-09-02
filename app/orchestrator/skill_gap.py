import json

from langchain_ollama import ChatOllama


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
    ):

        prompt = f"""
You are a career skill-gap analyzer.

CURRENT KNOWLEDGE:
{json.dumps(current_knowledge, ensure_ascii=False)}

MARKET REQUIREMENTS:
{market_analysis}

Compare the user's current knowledge against the actual market
requirements.

Return ONLY valid JSON in this exact structure:

{{
  "strengths": [],
  "gaps": [],
  "priorities": []
}}

Rules:
- strengths = skills the user already has that align with the market.
- gaps = important market skills missing from the user's knowledge.
- priorities = gaps ordered from highest to lowest importance.
- Do not invent requirements that are not present in the market analysis.
- Keep each item short.
"""

        response = await self.llm.ainvoke(prompt)

        content = response.content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        return json.loads(content)