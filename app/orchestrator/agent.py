import sys
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOB_MARKET_SERVER = (
    PROJECT_ROOT / "mcp_servers" / "job_market" / "server.py"
)


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

        self.llm = ChatOllama(
            model="llama3.2:1b",
            temperature=0,
        )

    async def initialize(self):
        self.tools = await self.client.get_tools()

    def _get_tool(self, name: str):
        for tool in self.tools:
            if tool.name == name:
                return tool

        raise RuntimeError(f"MCP tool '{name}' not found")

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
    ):
        if self.tools is None:
            await self.initialize()

        tool = self._get_tool("get_market_snapshot")

        result = await tool.ainvoke(
            {
                "role": role,
                "location": location,
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

                text = getattr(item, "text", None)
                if text:
                    return text

        text = getattr(result, "text", None)
        if text:
            return text

        return result

    async def analyze(
        self,
        role: str,
        location: str | None = None,
        specialization: str | None = None,
    ):
        snapshot = await self.get_market_snapshot(
            role=role,
            location=location,
        )

        if isinstance(snapshot, str):
            import json

            try:
                snapshot = json.loads(snapshot)
            except json.JSONDecodeError:
                snapshot = None

        if isinstance(snapshot, dict) and "text" in snapshot:
            import json

            try:
                snapshot = json.loads(snapshot["text"])
            except (TypeError, json.JSONDecodeError):
                snapshot = snapshot["text"]

        if not isinstance(snapshot, dict):
            return {
                "role": role,
                "location": location,
                "specialization": specialization,
                "jobs_found": 0,
                "jobs": [],
                "market_stats": {},
                "analysis": "Market data could not be parsed.",
            }

        if not snapshot.get("jobs"):
            return {
                "role": role,
                "location": location,
                "specialization": specialization,
                "jobs_found": 0,
                "jobs": [],
                "market_stats": snapshot.get("market_stats", {}),
                "analysis": (
                    "No matching jobs were found from the configured live sources. "
                    "Market analysis was not generated."
                ),
            }

        prompt = f"""
You are a career intelligence engine.

Analyze ONLY the following live job-market data.

TARGET ROLE:
{role}

LOCATION:
{location or "Any"}

SPECIALIZATION:
{specialization or "Not specified"}

LIVE MARKET DATA:
{snapshot}

Rules:
- Do not invent companies.
- Do not invent jobs.
- Do not invent salaries.
- Do not invent technologies.
- Do not invent requirements.
- Base factual claims only on the supplied job data.
- Clearly distinguish observations from facts.
- If the data is insufficient, say so.

Return:
1. Number of jobs analyzed
2. Companies represented
3. Locations
4. Frequently appearing skills
5. Frequently appearing technologies
6. Common experience requirements
7. Important observations
8. Data limitations
"""

        response = await self.llm.ainvoke(prompt)

        jobs = []

        if isinstance(snapshot, dict):
            jobs = snapshot.get("jobs", [])

        return {
            "role": role,
            "location": location,
            "specialization": specialization,
            "jobs_found": len(jobs),
            "jobs": jobs,
            "market_stats": (
                snapshot.get("market_stats", {})
                if isinstance(snapshot, dict)
                else {}
            ),
            "analysis": response.content,
        }

    async def generate_plan(
        self,
        profile,
    ):
        snapshot = await self.get_market_snapshot(
            role=profile.role,
            location=None,
        )

        prompt = f"""
You are the planning engine of an AI Engineering Career Command Center.

Create a personalized preparation plan using ONLY:

USER PROFILE:
Role: {profile.role}
Specialization: {profile.specialization}
Target companies: {profile.target_companies}
Preparation days: {profile.preparation_days}
Current knowledge: {profile.current_knowledge}

LIVE JOB MARKET DATA:
{snapshot}

Your goal is to identify what the user already knows versus what the
market requires, then create a realistic preparation roadmap.

Rules:
- Do not invent job requirements.
- Do not invent company requirements.
- Do not claim a skill is required unless it appears in the supplied
  market data.
- Do not recommend random technologies unrelated to the market data.
- Prioritize gaps that are supported by the retrieved postings.
- Respect the user's preparation time.
- Existing knowledge should not be treated as a learning gap.
- The plan must be practical and prioritized.

Return EXACTLY this structure:

EXECUTIVE SUMMARY

MARKET SIGNALS
- ...

CURRENT STRENGTHS
- ...

PRIORITY GAPS
- ...

LEARNING ROADMAP
Day 1:
- ...

Day 2:
- ...

Continue until the preparation period is covered.

PROJECT RECOMMENDATION
- ...

INTERVIEW PREPARATION
- ...

FINAL PRIORITIES
1. ...
2. ...
3. ...

DATA LIMITATIONS
- ...
"""

        response = await self.llm.ainvoke(prompt)

        return {
            "role": profile.role,
            "specialization": profile.specialization,
            "preparation_days": profile.preparation_days,
            "target_companies": profile.target_companies,
            "plan": response.content,
        }
