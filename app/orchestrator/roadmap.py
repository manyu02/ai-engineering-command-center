from app.orchestrator.models import RoadmapResult


class RoadmapGenerator:
    async def generate(
        self,
        role,
        specialization,
        preparation_days,
        current_knowledge,
        skill_gap,
        adaptive_learning=None,
    ) -> dict:
        gaps = skill_gap.get("gaps", [])
        adaptive_learning = adaptive_learning or {}

        high_priority = [
            gap["skill"]
            for gap in gaps
            if gap.get("priority") == "high"
        ]

        medium_priority = [
            gap["skill"]
            for gap in gaps
            if gap.get("priority") == "medium"
        ]

        adaptive_topics = adaptive_learning.get("focus_topics", [])

        priority_topics = []
        for topic in adaptive_topics + high_priority + medium_priority:
            if topic and topic not in priority_topics:
                priority_topics.append(topic)

        if not priority_topics:
            priority_topics = [
                "Python",
                "Prompt Engineering",
                "Cloud Deployment",
            ]

        cloud_priority = {
            "azure": 5,
            "aws": 4,
            "gcp": 4,
        }

        cloud_topics = [
            topic for topic in priority_topics
            if topic.lower() in cloud_priority
        ]

        primary_cloud = None
        if cloud_topics:
            primary_cloud = max(
                cloud_topics,
                key=lambda topic: cloud_priority[topic.lower()],
            )

        foundational_topics = [
            topic for topic in priority_topics
            if topic.lower() not in {"azure", "aws", "gcp", "cloud"}
        ]

        total_weeks = max(1, (preparation_days + 6) // 7)

        phases = [
            {
                "focus": "Close the highest-priority engineering gaps",
                "topics": foundational_topics[:2] or ["Python"],
                "project": f"Build a focused {role} implementation using {foundational_topics[0] if foundational_topics else 'Python'}",
            },
            {
                "focus": "Build cloud deployment capability",
                "topics": [primary_cloud or "Cloud Deployment"],
                "project": f"Deploy the {role} project using {primary_cloud or 'a cloud platform'}",
            },
            {
                "focus": "Build production-grade AI engineering capability",
                "topics": [
                    "AI System Integration",
                    "Evaluation",
                    "Observability",
                ],
                "project": f"Productionize and evaluate the {role} project",
            },
            {
                "focus": "Apply the complete skill stack in a capstone",
                "topics": [
                    specialization or "Generative AI",
                    "Production AI Engineering",
                ],
                "project": f"Build and document an end-to-end {role} capstone project",
            },
            {
                "focus": "Interview readiness and portfolio consolidation",
                "topics": [
                    "System Design",
                    "Technical Interview Practice",
                ],
                "project": f"Finalize and present the {role} portfolio project",
            },
        ]

        phases = phases[:total_weeks]

        weeks = []

        for index, phase in enumerate(phases, start=1):
            topics = phase["topics"]

            weeks.append({
                "week": index,
                "focus": phase["focus"],
                "topics": topics,
                "skills": topics,
                "projects": [phase["project"]],
                "resources": [
                    "Official documentation",
                    "Hands-on implementation",
                    "Real job requirements",
                ],
                "milestones": [
                    f"Demonstrate working knowledge of {topics[0]}"
                ],
                "deliverables": [
                    f"Working implementation related to {topics[0]}"
                ],
            })

        result = RoadmapResult(
            strategy=(
                f"Prepare for the {role} role through a progressive sequence "
                f"of foundational skill gaps, cloud deployment, production AI "
                f"engineering, capstone implementation and interview readiness."
            ),
            weeks=weeks,
        )

        return result.model_dump()
