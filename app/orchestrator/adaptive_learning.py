class AdaptiveLearning:

    def generate_adjustments(self, evaluation):
        score = evaluation.get("score", 0)
        missing_concepts = evaluation.get("missing_concepts", [])
        improvements = evaluation.get("improvements", [])

        if score < 5:
            priority = "high"
            recommendation = "Revisit the weak concepts before progressing."
        elif score < 8:
            priority = "medium"
            recommendation = "Practice the weak concepts and reinforce them with interview questions."
        else:
            priority = "low"
            recommendation = "Maintain the current level and continue with harder questions."

        return {
            "priority": priority,
            "focus_topics": missing_concepts,
            "practice_actions": improvements,
            "recommendation": recommendation,
            "score": score,
        }