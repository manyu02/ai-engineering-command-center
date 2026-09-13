import sys
import json
import re
from pathlib import Path
from collections import Counter

from app.profile_store import (
    load_roadmap,
    roadmap_fingerprint,
    save_roadmap,
)

from app.llm import create_llm
from langchain_mcp_adapters.client import MultiServerMCPClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOB_MARKET_SERVER = (
    PROJECT_ROOT / "mcp_servers" / "job_market" / "server.py"
)


SKILL_VOCABULARY = {
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "Go",
    "Rust",
    "R",
    "SQL",
    "NoSQL",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Generative AI",
    "Artificial Intelligence",
    "Data Science",
    "Data Engineering",
    "Data Analysis",
    "MLOps",
    "LLMs",
    "Large Language Models",
    "RAG",
    "Retrieval Augmented Generation",
    "Prompt Engineering",
    "Agentic AI",
    "AI Agents",
    "Model Evaluation",
    "Model Deployment",
    "ETL",
    "Data Warehousing",
    "Data Integration",
    "System Design",
    "Distributed Systems",
    "Cloud Computing",
    "DevOps",
    "Kubernetes",
    "Docker",
    "Git",
    "REST APIs",
    "Microservices",
    "Scalability",
    "Reliability",
    "Security",
}


TECHNOLOGY_VOCABULARY = {
    "PyTorch",
    "TensorFlow",
    "Keras",
    "Scikit-learn",
    "Hugging Face",
    "Transformers",
    "LangChain",
    "LangGraph",
    "LlamaIndex",
    "MCP",
    "OpenAI",
    "Anthropic",
    "Claude",
    "Claude Code",
    "Gemini",
    "Gemini CLI",
    "Codex",
    "Windsurf",
    "FAISS",
    "Milvus",
    "Pinecone",
    "Chroma",
    "Weaviate",
    "Azure",
    "AWS",
    "Google Cloud",
    "GCP",
    "Vertex AI",
    "Microsoft Foundry",
    "Databricks",
    "Snowflake",
    "Spark",
    "Kafka",
    "Airflow",
    "Docker",
    "Kubernetes",
    "Terraform",
    "GitHub",
    "GitLab",
    "Jenkins",
    "FastAPI",
    "Flask",
    "Django",
    "React",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
}


LEARNING_MAP = {
    "python": [
        "core Python and language fundamentals",
        "production Python patterns",
        "testing and debugging",
    ],
    "java": [
        "Java language fundamentals",
        "object-oriented application design",
        "testing and performance",
    ],
    "javascript": [
        "JavaScript language fundamentals",
        "asynchronous programming",
        "application testing and debugging",
    ],
    "typescript": [
        "TypeScript type system",
        "application architecture",
        "testing and maintainability",
    ],
    "c++": [
        "C++ language fundamentals",
        "memory and performance management",
        "testing and debugging",
    ],
    "c#": [
        "C# language fundamentals",
        ".NET application patterns",
        "testing and debugging",
    ],
    "go": [
        "Go language fundamentals",
        "concurrent application design",
        "testing and performance",
    ],
    "rust": [
        "Rust ownership and borrowing",
        "safe systems programming",
        "testing and performance",
    ],
    "sql": [
        "SQL querying and joins",
        "schema and query design",
        "query optimization",
    ],
    "nosql": [
        "NoSQL data modeling",
        "query and indexing patterns",
        "consistency and scalability",
    ],
    "machine learning": [
        "supervised and unsupervised learning",
        "feature engineering and model selection",
        "model evaluation",
    ],
    "deep learning": [
        "neural network architectures",
        "training and optimization",
        "model evaluation",
    ],
    "natural language processing": [
        "text representation",
        "language-model pipelines",
        "NLP evaluation",
    ],
    "computer vision": [
        "image representation",
        "vision model architectures",
        "model evaluation",
    ],
    "generative ai": [
        "generative model fundamentals",
        "LLM application architecture",
        "evaluation and reliability",
    ],
    "data science": [
        "data exploration",
        "statistical modeling",
        "model evaluation",
    ],
    "data engineering": [
        "data pipeline architecture",
        "data transformation",
        "pipeline reliability",
    ],
    "data analysis": [
        "data exploration",
        "analytical querying",
        "communicating analytical results",
    ],
    "mlops": [
        "ML pipeline architecture",
        "model deployment",
        "monitoring and reliability",
    ],
    "llms": [
        "LLM architecture and capabilities",
        "LLM application patterns",
        "evaluation and reliability",
    ],
    "large language models": [
        "LLM architecture and capabilities",
        "LLM application patterns",
        "evaluation and reliability",
    ],
    "rag": [
        "retrieval pipeline architecture",
        "chunking and embedding strategies",
        "retrieval evaluation",
    ],
    "retrieval augmented generation": [
        "retrieval pipeline architecture",
        "chunking and embedding strategies",
        "retrieval evaluation",
    ],
    "prompt engineering": [
        "prompt structure and instruction design",
        "structured outputs",
        "prompt evaluation",
    ],
    "agentic ai": [
        "agent architecture",
        "tool use and workflow orchestration",
        "agent evaluation",
    ],
    "ai agents": [
        "agent architecture",
        "tool use and workflow orchestration",
        "agent evaluation",
    ],
    "model evaluation": [
        "evaluation criteria and datasets",
        "automated evaluation",
        "error analysis",
    ],
    "model deployment": [
        "model serving architecture",
        "deployment strategies",
        "production monitoring",
    ],
    "system design": [
        "service and component architecture",
        "scalability and reliability",
        "design trade-offs",
    ],
    "distributed systems": [
        "distributed architecture",
        "consistency and communication",
        "failure handling",
    ],
    "cloud computing": [
        "cloud architecture fundamentals",
        "deployment and infrastructure",
        "scaling and reliability",
    ],
    "devops": [
        "CI/CD architecture",
        "deployment automation",
        "monitoring and reliability",
    ],
    "kubernetes": [
        "Kubernetes architecture",
        "workloads and networking",
        "deployment and scaling",
    ],
    "docker": [
        "container fundamentals",
        "image and container design",
        "containerized deployment",
    ],
    "rest apis": [
        "REST API design",
        "authentication and validation",
        "API testing and reliability",
    ],
    "microservices": [
        "microservice architecture",
        "service communication",
        "resilience and observability",
    ],
    "scalability": [
        "horizontal and vertical scaling",
        "bottleneck analysis",
        "capacity planning",
    ],
    "reliability": [
        "failure modes",
        "monitoring and alerting",
        "resilience patterns",
    ],
    "security": [
        "application security fundamentals",
        "authentication and authorization",
        "security testing",
    ],
    "pytorch": [
        "PyTorch tensors and models",
        "training workflows",
        "model evaluation",
    ],
    "tensorflow": [
        "TensorFlow model construction",
        "training pipelines",
        "model evaluation",
    ],
    "scikit-learn": [
        "estimator and pipeline design",
        "model selection",
        "evaluation and validation",
    ],
    "hugging face": [
        "transformer model usage",
        "fine-tuning workflows",
        "model evaluation",
    ],
    "transformers": [
        "transformer architecture",
        "model inference",
        "fine-tuning and evaluation",
    ],
    "langchain": [
        "LangChain components",
        "tool and chain orchestration",
        "application evaluation",
    ],
    "langgraph": [
        "graph-based agent workflows",
        "state and tool management",
        "workflow evaluation",
    ],
    "llamaindex": [
        "indexing pipelines",
        "retrieval architecture",
        "retrieval evaluation",
    ],
    "mcp": [
        "MCP architecture",
        "tools and resource integration",
        "MCP client-server workflows",
    ],
    "openai": [
        "API integration",
        "structured model outputs",
        "production API usage",
    ],
    "anthropic": [
        "API integration",
        "structured model outputs",
        "production API usage",
    ],
    "azure": [
        "Azure architecture fundamentals",
        "Azure deployment patterns",
        "monitoring and scaling",
    ],
    "aws": [
        "AWS architecture fundamentals",
        "AWS deployment patterns",
        "monitoring and scaling",
    ],
    "google cloud": [
        "Google Cloud architecture",
        "cloud deployment patterns",
        "monitoring and scaling",
    ],
    "gcp": [
        "Google Cloud architecture",
        "cloud deployment patterns",
        "monitoring and scaling",
    ],
    "vertex ai": [
        "Vertex AI model workflows",
        "deployment and serving",
        "evaluation and monitoring",
    ],
    "microsoft foundry": [
        "Microsoft Foundry architecture",
        "model and agent deployment",
        "evaluation and monitoring",
    ],
    "databricks": [
        "Databricks data architecture",
        "data and ML workflows",
        "production deployment",
    ],
    "snowflake": [
        "Snowflake architecture",
        "data modeling and querying",
        "performance optimization",
    ],
    "spark": [
        "Spark processing model",
        "distributed data transformations",
        "performance optimization",
    ],
    "kafka": [
        "Kafka architecture",
        "event streaming",
        "reliability and scaling",
    ],
    "airflow": [
        "Airflow DAG design",
        "workflow orchestration",
        "pipeline monitoring",
    ],
    "terraform": [
        "Terraform configuration",
        "infrastructure modules",
        "state and deployment management",
    ],
    "fastapi": [
        "FastAPI application design",
        "validation and dependency management",
        "API testing and deployment",
    ],
    "flask": [
        "Flask application architecture",
        "API design",
        "testing and deployment",
    ],
    "django": [
        "Django application architecture",
        "data and API design",
        "testing and deployment",
    ],
    "react": [
        "React component architecture",
        "state and data management",
        "frontend testing",
    ],
    "postgresql": [
        "PostgreSQL schema design",
        "querying and indexing",
        "performance optimization",
    ],
    "mysql": [
        "MySQL schema design",
        "querying and indexing",
        "performance optimization",
    ],
    "mongodb": [
        "MongoDB data modeling",
        "queries and indexing",
        "scaling and reliability",
    ],
    "redis": [
        "Redis data structures",
        "caching patterns",
        "performance and reliability",
    ],
    "git": [
        "Git workflows",
        "branching and collaboration",
        "history management",
    ],
    "github": [
        "GitHub collaboration workflows",
        "pull requests and code review",
        "repository management",
    ],
    "gitlab": [
        "GitLab collaboration workflows",
        "CI/CD pipelines",
        "repository management",
    ],
    "jenkins": [
        "Jenkins pipeline design",
        "CI/CD automation",
        "deployment reliability",
    ],
    "terraform": [
        "Terraform configuration",
        "infrastructure modules",
        "state and deployment management",
    ],
}


class JobMarketAgent:

    def __init__(self):
        self.client = MultiServerMCPClient(
            {
                "job_market": {
                    "transport": "stdio",
                    "command": sys.executable,
                    "args": [str(JOB_MARKET_SERVER)],
                    "cwd": str(PROJECT_ROOT),
                }
            }
        )

        self.tools = None

        self.llm = create_llm()

    async def initialize(self):
        self.tools = await self.client.get_tools()

    def _get_tool(self, name: str):
        for tool in self.tools:
            if tool.name == name:
                return tool

        raise RuntimeError(
            f"MCP tool '{name}' not found"
        )

    async def search_jobs(
        self,
        role: str,
        location: str | None = None,
    ):
        if self.tools is None:
            await self.initialize()

        tool = self._get_tool("search_jobs")

        return await tool.ainvoke(
            {
                "role": role,
                "location": location,
            }
        )

    async def get_market_snapshot(
        self,
        role: str,
        location: str | None = None,
        specialization: str | None = None,
    ):
        if self.tools is None:
            await self.initialize()

        tool = self._get_tool(
            "get_market_snapshot"
        )

        result = await tool.ainvoke(
            {
                "role": role,
                "location": location,
                "specialization": specialization,
                "max_jobs": 10,
            }
        )

        if isinstance(result, dict):
            return result

        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    if "text" in item:
                        return item["text"]

                    return item

                text = getattr(
                    item,
                    "text",
                    None,
                )

                if text:
                    return text

        text = getattr(
            result,
            "text",
            None,
        )

        if text:
            return text

        return result

    def _normalize_text(
        self,
        text,
    ):
        if not text:
            return ""

        text = str(text).lower()
        text = re.sub(
            r"[\u2010-\u2015]",
            "-",
            text,
        )

        return text

    def _contains_term(
        self,
        text,
        term,
    ):
        normalized_text = self._normalize_text(
            text
        )

        normalized_term = self._normalize_text(
            term
        )

        if not normalized_term:
            return False

        if len(normalized_term) <= 3:
            return (
                re.search(
                    rf"\b{re.escape(normalized_term)}\b",
                    normalized_text,
                )
                is not None
            )

        return normalized_term in normalized_text

    def _extract_frequency(
        self,
        jobs,
        vocabulary,
    ):
        counts = Counter()

        for item in jobs:
            job = item.get(
                "job",
                {},
            )

            text = " ".join(
                [
                    job.get("title") or "",
                    job.get("description") or "",
                ]
            )

            for term in vocabulary:
                if self._contains_term(
                    text,
                    term,
                ):
                    counts[term] += 1

        return [
            {
                "name": name,
                "job_count": count,
            }
            for name, count in counts.most_common()
        ]

    def _extract_experience_requirements(
        self,
        jobs,
    ):
        patterns = [
            r"\b\d+\+?\s*(?:years?|yrs?)\b",
            r"\bat least \d+\s*(?:years?|yrs?)\b",
            r"\b\d+\s*-\s*\d+\s*(?:years?|yrs?)\b",
        ]

        requirements = Counter()

        for item in jobs:
            job = item.get(
                "job",
                {},
            )

            description = (
                job.get("description")
                or ""
            )

            for pattern in patterns:
                matches = re.findall(
                    pattern,
                    description,
                    flags=re.IGNORECASE,
                )

                for match in matches:
                    normalized = (
                        " ".join(
                            match.split()
                        ).lower()
                    )

                    requirements[
                        normalized
                    ] += 1

        return [
            {
                "requirement": requirement,
                "job_count": count,
            }
            for requirement, count
            in requirements.most_common()
        ]

    def _build_market_facts(
        self,
        snapshot,
    ):
        jobs = snapshot.get(
            "jobs",
            [],
        )

        companies = sorted(
            {
                item.get(
                    "job",
                    {},
                ).get("company")
                for item in jobs
                if item.get(
                    "job",
                    {},
                ).get("company")
            }
        )

        locations = sorted(
            {
                item.get(
                    "job",
                    {},
                ).get("location")
                for item in jobs
                if item.get(
                    "job",
                    {},
                ).get("location")
            }
        )

        skills = self._extract_frequency(
            jobs,
            SKILL_VOCABULARY,
        )

        technologies = self._extract_frequency(
            jobs,
            TECHNOLOGY_VOCABULARY,
        )

        experience_requirements = (
            self._extract_experience_requirements(
                jobs
            )
        )

        return {
            "jobs_analyzed": len(jobs),
            "companies": companies,
            "locations": locations,
            "skills": skills,
            "technologies": technologies,
            "experience_requirements": (
                experience_requirements
            ),
        }

    async def analyze(
        self,
        role: str,
        location: str | None = None,
        specialization: str | None = None,
    ):
        snapshot = await self.get_market_snapshot(
            role=role,
            location=location,
            specialization=specialization,
        )

        if isinstance(snapshot, str):
            try:
                snapshot = json.loads(
                    snapshot
                )
            except json.JSONDecodeError:
                snapshot = None

        if (
            isinstance(snapshot, dict)
            and "text" in snapshot
        ):
            try:
                snapshot = json.loads(
                    snapshot["text"]
                )
            except (
                TypeError,
                json.JSONDecodeError,
            ):
                snapshot = snapshot["text"]

        if not isinstance(
            snapshot,
            dict,
        ):
            return {
                "role": role,
                "location": location,
                "specialization": specialization,
                "jobs_found": 0,
                "jobs": [],
                "market_stats": {},
                "analysis": (
                    "Market data could not be parsed."
                ),
            }

        if not snapshot.get("jobs"):
            return {
                "role": role,
                "location": location,
                "specialization": specialization,
                "jobs_found": 0,
                "jobs": [],
                "market_stats": snapshot.get(
                    "market_stats",
                    {},
                ),
                "analysis": (
                    "No matching jobs were found "
                    "from the configured live sources. "
                    "Market analysis was not generated."
                ),
            }

        market_facts = self._build_market_facts(
            snapshot
        )

        skills = market_facts.get(
            "skills",
            [],
        )

        technologies = market_facts.get(
            "technologies",
            [],
        )

        experience_requirements = (
            market_facts.get(
                "experience_requirements",
                [],
            )
        )

        top_skills = skills[:8]
        top_technologies = technologies[:8]
        top_experience = (
            experience_requirements[:5]
        )

        companies = market_facts.get(
            "companies",
            [],
        )

        locations = market_facts.get(
            "locations",
            [],
        )

        analysis_sections = [
            "MARKET SUMMARY",
            (
                f"- {market_facts['jobs_analyzed']} "
                f"matching jobs were analyzed across "
                f"{len(companies)} companies."
            ),
            (
                "- Retrieved locations include: "
                f"{', '.join(locations) if locations else 'not specified'}."
            ),
            "",
            "KEY SKILLS",
        ]

        if top_skills:
            for item in top_skills:
                analysis_sections.append(
                    f"- {item['name']}: appears in "
                    f"{item['job_count']} jobs."
                )
        else:
            analysis_sections.append(
                "- No supported skill signals were extracted."
            )

        analysis_sections.extend(
            [
                "",
                "KEY TECHNOLOGIES",
            ]
        )

        if top_technologies:
            for item in top_technologies:
                analysis_sections.append(
                    f"- {item['name']}: appears in "
                    f"{item['job_count']} jobs."
                )
        else:
            analysis_sections.append(
                "- No supported technology signals were extracted."
            )

        analysis_sections.extend(
            [
                "",
                "EXPERIENCE SIGNALS",
            ]
        )

        if top_experience:
            for item in top_experience:
                analysis_sections.append(
                    f"- {item['requirement']}: appears in "
                    f"{item['job_count']} jobs."
                )
        else:
            analysis_sections.append(
                "- No explicit experience requirements were extracted."
            )

        analysis_sections.extend(
            [
                "",
                "IMPORTANT OBSERVATIONS",
                (
                    "- Rankings are based on role, "
                    "specialization, and location "
                    "relevance scores."
                ),
                (
                    "- Skill and technology frequencies "
                    "are calculated from the retrieved "
                    "job descriptions and titles."
                ),
                "",
                "DATA LIMITATIONS",
                (
                    "- This analysis reflects only the "
                    "retrieved matching postings and "
                    "supported vocabulary."
                ),
                (
                    "- Missing job descriptions or "
                    "unspecified locations can reduce "
                    "the available signals."
                ),
            ]
        )

        analysis = "\n".join(
            analysis_sections
        )

        jobs = snapshot.get(
            "jobs",
            [],
        )

        compact_jobs = []

        for item in jobs:
            job = item.get(
                "job",
                {},
            )

            compact_jobs.append(
                {
                    "company": job.get(
                        "company"
                    ),
                    "title": job.get(
                        "title"
                    ),
                    "location": job.get(
                        "location"
                    ),
                    "url": job.get(
                        "url"
                    ),
                    "source": job.get(
                        "source"
                    ),
                    "published_at": job.get(
                        "published_at"
                    ),
                    "description": (
                        job.get(
                            "description"
                        )
                        or ""
                    )[:2000],
                    "relevance_score": item.get(
                        "relevance_score",
                        0,
                    ),
                    "role_score": item.get(
                        "role_score",
                        0,
                    ),
                    "specialization_score": item.get(
                        "specialization_score",
                        0,
                    ),
                    "location_score": item.get(
                        "location_score",
                        0,
                    ),
                }
            )

        return {
            "role": role,
            "location": location,
            "specialization": specialization,
            "jobs_found": len(
                compact_jobs
            ),
            "jobs": compact_jobs,
            "market_stats": snapshot.get(
                "market_stats",
                {},
            ),
            "analysis": analysis,
        }

    def _knowledge_covers(
        self,
        topic,
        current_knowledge,
    ):
        normalized_topic = self._normalize_text(
            topic
        )

        knowledge_text = self._normalize_text(
            " ".join(current_knowledge)
        )

        if not normalized_topic:
            return False

        if self._contains_term(
            knowledge_text,
            normalized_topic,
        ):
            return True

        topic_tokens = {
            token
            for token in re.findall(
                r"[a-z0-9+#.-]+",
                normalized_topic,
            )
            if len(token) > 2
        }

        knowledge_tokens = {
            token
            for token in re.findall(
                r"[a-z0-9+#.-]+",
                knowledge_text,
            )
            if len(token) > 2
        }

        return bool(
            topic_tokens
            and topic_tokens.issubset(
                knowledge_tokens
            )
        )

    def _learning_subtopics(
        self,
        topic,
    ):
        key = self._normalize_text(
            topic
        )

        if key in LEARNING_MAP:
            return list(
                LEARNING_MAP[key]
            )

        for mapped_topic, subtopics in LEARNING_MAP.items():
            if (
                self._contains_term(
                    key,
                    mapped_topic,
                )
                or self._contains_term(
                    mapped_topic,
                    key,
                )
            ):
                return list(
                    subtopics
                )

        return [
            f"{topic} fundamentals and core concepts",
            f"{topic} implementation patterns",
            f"{topic} testing, evaluation, and trade-offs",
        ]

    def _extract_market_requirements(
        self,
        jobs,
        current_knowledge,
    ):
        vocabulary = {}

        for term in SKILL_VOCABULARY:
            vocabulary[
                self._normalize_text(term)
            ] = term

        for term in TECHNOLOGY_VOCABULARY:
            vocabulary[
                self._normalize_text(term)
            ] = term

        counts = Counter()

        for item in jobs:
            if not isinstance(
                item,
                dict,
            ):
                continue

            job = item.get(
                "job",
                {},
            )

            if not isinstance(
                job,
                dict,
            ):
                continue

            text = " ".join(
                [
                    str(
                        job.get(
                            "title"
                        )
                        or ""
                    ),
                    str(
                        job.get(
                            "description"
                        )
                        or ""
                    ),
                ]
            )

            for normalized_term, canonical_term in vocabulary.items():
                if self._contains_term(
                    text,
                    normalized_term,
                ):
                    counts[
                        canonical_term
                    ] += 1

        requirements = []

        for topic, job_count in counts.most_common():
            if self._knowledge_covers(
                topic,
                current_knowledge,
            ):
                continue

            requirements.append(
                {
                    "topic": topic,
                    "job_count": job_count,
                    "learn": self._learning_subtopics(
                        topic
                    ),
                }
            )

        return requirements

    def _allocate_days(
        self,
        requirements,
        days,
    ):
        if not requirements:
            return []

        weights = [
            max(
                requirement["job_count"],
                1,
            )
            for requirement in requirements
        ]

        total_weight = sum(
            weights
        )

        allocations = []

        for requirement, weight in zip(
            requirements,
            weights,
        ):
            raw = (
                days
                * weight
                / total_weight
            )

            allocations.append(
                {
                    "requirement": requirement,
                    "raw": raw,
                    "days": max(
                        1,
                        int(raw),
                    ),
                }
            )

        if len(allocations) > days:
            allocations.sort(
                key=lambda item: (
                    item["requirement"][
                        "job_count"
                    ],
                    item["raw"],
                )
            )

            while (
                len(allocations)
                > days
            ):
                allocations.pop(0)

        allocated = sum(
            item["days"]
            for item in allocations
        )

        while allocated > days:
            candidates = [
                item
                for item in allocations
                if item["days"] > 1
            ]

            if not candidates:
                break

            candidates.sort(
                key=lambda item: (
                    item["days"],
                    item["requirement"][
                        "job_count"
                    ],
                ),
                reverse=True,
            )

            candidates[0]["days"] -= 1
            allocated -= 1

        while allocated < days:
            allocations.sort(
                key=lambda item: (
                    item["raw"]
                    - item["days"],
                    item["requirement"][
                        "job_count"
                    ],
                ),
                reverse=True,
            )

            allocations[0]["days"] += 1
            allocated += 1

        allocations.sort(
            key=lambda item: (
                item["requirement"][
                    "job_count"
                ],
                item["raw"],
            ),
            reverse=True,
        )

        return allocations

    async def generate_plan(
        self,
        profile,
    ):
        days = int(profile.preparation_days)

        if days < 1:
            raise ValueError(
                "Preparation days must be greater than zero."
            )

        fingerprint = roadmap_fingerprint(profile)

        cached = load_roadmap(fingerprint)

        if cached is not None:
            cached_roadmap = cached.get("roadmap", [])

            if (
                cached.get("preparation_days") == days
                and isinstance(cached_roadmap, list)
                and len(cached_roadmap) == days
            ):
                cached["cached"] = True
                return cached

        snapshot = await self.get_market_snapshot(
            role=profile.role,
            location=None,
            specialization=profile.specialization,
        )

        if isinstance(snapshot, str):
            snapshot = snapshot.strip()

            if snapshot.startswith("```"):
                snapshot = snapshot.removeprefix("```json")
                snapshot = snapshot.removeprefix("```")
                snapshot = snapshot.removesuffix("```").strip()

            try:
                snapshot = json.loads(snapshot)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Market snapshot returned invalid JSON."
                ) from exc

        if not isinstance(snapshot, dict):
            raise ValueError(
                "Market snapshot must be a JSON object."
            )

        jobs = snapshot.get("jobs", [])

        if not isinstance(jobs, list) or not jobs:
            raise ValueError(
                "No relevant job-market data was found for roadmap generation."
            )

        current_knowledge = [
            str(topic).strip()
            for topic in profile.current_knowledge
            if str(topic).strip()
        ]

        requirements = self._extract_market_requirements(
            jobs,
            current_knowledge,
        )

        if not requirements:
            raise ValueError(
                "No new technical market requirements were found outside the current knowledge profile."
            )

        requirements = requirements[:12]

        allocations = self._allocate_days(
            requirements,
            days,
        )

        if not allocations:
            raise ValueError(
                "Unable to allocate preparation days."
            )

        maximum_frequency = max(
            requirement["job_count"]
            for requirement in requirements
        )

        for requirement in requirements:
            frequency = requirement["job_count"]

            ratio = frequency / maximum_frequency

            if ratio >= 0.75:
                priority = "high"
            elif ratio >= 0.40:
                priority = "medium"
            else:
                priority = "low"

            requirement["frequency"] = (
                f"{frequency}/{len(jobs)}"
            )

            requirement["priority"] = priority

        roadmap = []

        for allocation in allocations:
            requirement = allocation["requirement"]

            topic = requirement["topic"]
            frequency = requirement["frequency"]
            learn_items = requirement["learn"]
            assigned_days = allocation["days"]

            for index in range(assigned_days):
                if index < len(learn_items):
                    learn_topic = learn_items[index]
                    day_topic = topic
                else:
                    learn_topic = (
                        "Applied practice: "
                        f"{learn_items[index % len(learn_items)]}"
                    )
                    day_topic = (
                        f"{topic} — Applied Practice"
                    )

                roadmap.append(
                    {
                        "day": len(roadmap) + 1,
                        "topic": day_topic,
                        "why": (
                            f"Required by "
                            f"{frequency} relevant jobs."
                        ),
                        "learn": [learn_topic],
                    }
                )

        if len(roadmap) > days:
            roadmap = roadmap[:days]

        if len(roadmap) < days:
            strongest = allocations[0]["requirement"]

            while len(roadmap) < days:
                index = (
                    len(roadmap)
                    % len(strongest["learn"])
                )

                roadmap.append(
                    {
                        "day": len(roadmap) + 1,
                        "topic": (
                            f"{strongest['topic']} "
                            f"— Applied Practice"
                        ),
                        "why": (
                            f"Required by "
                            f"{strongest['frequency']} "
                            f"relevant jobs."
                        ),
                        "learn": [
                            (
                                "Apply "
                                f"{strongest['learn'][index]} "
                                "to a realistic problem"
                            )
                        ],
                    }
                )

        if len(roadmap) != days:
            raise RuntimeError(
                f"Roadmap generation produced {len(roadmap)} days "
                f"for a {days}-day preparation plan."
            )

        market_signals = []

        for requirement in requirements[:8]:
            market_signals.append(
                (
                    f"{requirement['topic']} appears in "
                    f"{requirement['job_count']}/"
                    f"{len(jobs)} relevant jobs."
                )
            )

        priority_gaps = []

        for requirement in requirements[:5]:
            priority_gaps.append(
                {
                    "skill": requirement["topic"],
                    "reason": (
                        f"Required by "
                        f"{requirement['job_count']}/"
                        f"{len(jobs)} relevant jobs "
                        f"and not clearly covered by "
                        f"the current knowledge profile."
                    ),
                    "priority": requirement["priority"],
                }
            )

        result = {
            "role": profile.role,
            "specialization": profile.specialization,
            "preparation_days": days,
            "target_companies": profile.target_companies,
            "current_knowledge": profile.current_knowledge,
            "market_jobs_analyzed": len(jobs),
            "market_signals": market_signals,
            "priority_gaps": priority_gaps,
            "roadmap": roadmap,
            "cached": False,
        }

        save_roadmap(
            fingerprint,
            result,
        )

        return result