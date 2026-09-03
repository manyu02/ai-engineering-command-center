from app.orchestrator.rag import RAGEngine


class InterviewAgent:

    def __init__(self, llm):
        self.llm = llm
        self.rag = RAGEngine()

    async def generate_question(self, role, specialization=None):
        context = self.rag.format_context(
            f"{role} {specialization or ''}"
        )

        prompt = f"""
You are an AI engineering interviewer.

Role: {role}
Specialization: {specialization}

Knowledge context:
{context}

Generate one realistic interview question.
Return only the question.
"""

        response = await self.llm.ainvoke(prompt)

        return {
            "question": response.content.strip()
        }
