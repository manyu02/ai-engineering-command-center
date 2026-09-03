import json
from pathlib import Path


class KnowledgeRetriever:

    def __init__(self):
        path = Path(__file__).parent / "data.json"
        self.documents = json.loads(path.read_text(encoding="utf-8"))

    def search(self, query: str, limit: int = 3):
        words = set(query.lower().split())

        scored = []

        for document in self.documents:
            text = (
                document["topic"] + " " + document["content"]
            ).lower()

            score = sum(word in text for word in words)

            if score:
                scored.append((score, document))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [document for _, document in scored[:limit]]
