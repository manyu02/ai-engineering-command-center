from app.orchestrator.models import SkillGapResult


class SkillGapAnalyzer:
    async def analyze(self, current_knowledge: list[str], market_analysis: str) -> dict:
        known = {item.strip().lower() for item in current_knowledge if item.strip()}

        skills = [
            ("Python", "intermediate", "high"),
            ("LLMs", "intermediate", "high"),
            ("RAG", "intermediate", "high"),
            ("Agents", "intermediate", "high"),
            ("MCP", "intermediate", "high"),
            ("LangChain", "intermediate", "medium"),
            ("Prompt Engineering", "intermediate", "medium"),
            ("Vector Databases", "intermediate", "medium"),
            ("FastAPI", "intermediate", "medium"),
            ("Docker", "intermediate", "medium"),
            ("Kubernetes", "intermediate", "low"),
            ("Cloud", "intermediate", "medium"),
            ("AWS", "intermediate", "medium"),
            ("Azure", "intermediate", "medium"),
            ("GCP", "intermediate", "medium"),
        ]

        gaps = []

        for skill, required_level, priority in skills:
            if skill.lower() in known:
                continue

            if skill.lower() not in market_analysis.lower():
                continue

            gaps.append({
                "skill": skill,
                "current_level": "beginner",
                "required_level": required_level,
                "gap": f"{skill} is relevant to the current market requirements but is not listed in the candidate's current knowledge.",
                "priority": priority,
            })

        result = SkillGapResult(
            summary=(
                "Focus on the highest-priority market skills that are not yet "
                "covered by the candidate's current knowledge."
            ),
            gaps=gaps[:8],
        )

        return result.model_dump()