import re


class CandidateIntelligence:

    SKILL_ALIASES = {
        "llms": ["llm", "llms", "large language model", "large language models"],
        "agents": ["agent", "agents", "agentic", "agentic ai", "ai agents"],
        "rag": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
        "mcp": ["mcp", "model context protocol"],
        "langchain": ["langchain"],
        "python": ["python"],
        "javascript": ["javascript"],
        "typescript": ["typescript"],
        "react": ["react", "react.js", "reactjs"],
        "fastapi": ["fastapi"],
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "aws": ["aws", "amazon web services"],
        "azure": ["azure", "microsoft azure"],
        "gcp": ["gcp", "google cloud", "google cloud platform"],
        "sql": ["sql"],
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning"],
        "generative ai": ["generative ai", "genai"],
        "prompt engineering": ["prompt engineering", "prompt design"],
        "vector database": [
            "vector database",
            "vector databases",
            "vector db",
            "vector search",
        ],
    }

    def analyze(self, current_knowledge, jobs):
        knowledge = {
            self._normalize_skill(item)
            for item in current_knowledge
            if item and item.strip()
        }

        results = []

        for job in jobs:
            title = job.get("title", "")
            description = job.get("description", "")
            text = f"{title} {description}".lower()

            matched = [
                skill
                for skill in sorted(knowledge)
                if self._skill_in_text(skill, text)
            ]

            job_skills = self._extract_skills(text)

            missing = [
                skill
                for skill in job_skills
                if skill not in knowledge and skill not in matched
            ]

            title_matches = [
                skill
                for skill in matched
                if self._skill_in_text(skill, title.lower())
            ]

            description_matches = [
                skill
                for skill in matched
                if skill not in title_matches
            ]

            score = (
                len(title_matches) * 15
                + len(description_matches) * 10
            )

            if matched:
                score = max(score, 15)

            results.append({
                "job_title": title,
                "company": job.get("company"),
                "fit_score": min(round(score, 2), 100),
                "matching_skills": matched,
                "missing_skills": missing[:10],
            })

        results.sort(
            key=lambda item: item["fit_score"],
            reverse=True,
        )

        return {
            "candidate_skills": sorted(knowledge),
            "job_matches": results,
        }

    def _normalize_skill(self, skill):
        normalized = skill.lower().strip()

        aliases = {
            "llm": "llms",
            "large language model": "llms",
            "large language models": "llms",
            "ai agents": "agents",
            "agentic ai": "agents",
            "genai": "generative ai",
            "ml": "machine learning",
            "k8s": "kubernetes",
            "vector db": "vector database",
            "vector databases": "vector database",
        }

        return aliases.get(normalized, normalized)

    def _skill_in_text(self, skill, text):
        aliases = self.SKILL_ALIASES.get(skill, [skill])

        return any(
            re.search(
                rf"\b{re.escape(alias)}\b",
                text,
            )
            for alias in aliases
        )

    def _extract_skills(self, text):
        return [
            skill
            for skill in self.SKILL_ALIASES
            if self._skill_in_text(skill, text)
        ]