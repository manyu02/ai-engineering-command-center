from app.orchestrator.rag import RAGEngine


class InterviewAgent:

    def __init__(self, llm):
        self.llm = llm
        self.rag = RAGEngine()

    async def generate_question(
        self,
        role,
        specialization=None,
        history=None,
    ):
        history = history or []

        context = self.rag.format_context(
            f"{role} {specialization or ''}"
        )

        conversation = "\n".join(
            f"Question: {item.get('question', '')}\n"
            f"Answer: {item.get('answer', '')}"
            for item in history
        )

        prompt = f"""
You are conducting a realistic technical interview.

Target role: {role}
Specialization: {specialization or "General"}

Knowledge context:
{context}

Previous interview conversation:
{conversation or "No previous questions. Start the interview."}

Your task is to ask the next interview question.

Rules:
- Ask exactly one question.
- Make it relevant to the target role.
- Use the specialization when provided.
- Do not repeat a previous question.
- If previous answers reveal a weakness, probe that area naturally.
- Increase or decrease difficulty based on the candidate's demonstrated understanding.
- Mix conceptual, practical, problem-solving, system-design, and scenario questions where appropriate.
- Do not provide the answer.
- Do not provide explanations or feedback.
- Return only the interview question.
"""

        response = await self.llm.ainvoke(prompt)

        return {
            "question": response.content.strip()
        }