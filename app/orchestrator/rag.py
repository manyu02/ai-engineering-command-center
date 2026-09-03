from app.knowledge.retriever import KnowledgeRetriever


class RAGEngine:

    def __init__(self):
        self.retriever = KnowledgeRetriever()

    def retrieve(self, query: str, limit: int = 3):
        return self.retriever.search(query, limit)

    def format_context(self, query: str, limit: int = 3):
        documents = self.retrieve(query, limit)

        return "\n\n".join(
            f"{doc['topic']}: {doc['content']}"
            for doc in documents
        )
