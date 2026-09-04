class AdaptiveLearning:

    def generate_adjustments(self, evaluation):
        score = evaluation.get("score", 0)
        missing_concepts = evaluation.get("missing_concepts", [])
        improvements = evaluation.get("improvements", [])

        if score < 5:
            priority = "high"
        elif score < 8:
            priority = "medium"
        else:
            priority = "low"

        return {
            "priority": priority,
            "focus_topics": missing_concepts,
            "practice_actions": improvements,
            "score": score,
        }
