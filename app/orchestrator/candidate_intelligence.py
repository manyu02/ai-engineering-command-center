import re


class CandidateIntelligence:

    def analyze(self, current_knowledge, jobs):
        knowledge = {
            item.lower().strip()
            for item in current_knowledge
            if item.strip()
        }

        results = []

        for job in jobs:
            text = f"{job.get('title', '')} {job.get('description', '')}".lower()

            matched = [
                skill for skill in knowledge
                if skill in text
            ]

            missing = [
                skill for skill in self._extract_skills(text)
                if skill not in knowledge
            ]

            score = round(
                (len(matched) / max(len(knowledge), 1)) * 100,
                2,
            )

            results.append({
                "job_title": job.get("title"),
                "company": job.get("company"),
                "fit_score": min(score, 100),
                "matching_skills": matched,
                "missing_skills": missing[:10],
            })

        return {
            "candidate_skills": sorted(knowledge),
            "job_matches": results,
        }

    def _extract_skills(self, text):
        skills = [
            "python",
            "javascript",
            "typescript",
            "react",
            "fastapi",
            "langchain",
            "llm",
            "rag",
            "agents",
            "mcp",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "sql",
            "machine learning",
            "deep learning",
            "generative ai",
            "prompt engineering",
            "vector database",
        ]

        return [
            skill for skill in skills
            if re.search(rf"\b{re.escape(skill)}\b", text)
        ]
