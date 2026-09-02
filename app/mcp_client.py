import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama


load_dotenv()


async def main():

    project_root = Path(__file__).resolve().parent.parent

    server_path = (
        project_root
        / "mcp_servers"
        / "job_market"
        / "server.py"
    )

    client = MultiServerMCPClient(
        {
            "job_market": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(server_path)],
                "cwd": str(project_root),
            }
        }
    )

    print("1. Loading MCP tools...")

    tools = await client.get_tools()

    print("2. MCP tools loaded:")

    for tool in tools:
        print(f"   - {tool.name}")

    print("\n3. Creating local LLM...")

    model = ChatOllama(
        model="llama3.2:1b",
        temperature=0,
    )

    print("4. Local LLM created.")

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
You are the Job Market Intelligence Agent for the AI Engineering Command Center.

Your job is to analyze REAL job-market data.

IMPORTANT RULES:

1. When the user asks about jobs, always use the available MCP job-market tools.

2. Prefer get_market_snapshot when the user asks for market trends,
   skills, requirements, or an overview of a role.

3. Treat returned job data as the source of truth.

4. NEVER invent:
   - companies
   - job titles
   - salaries
   - locations
   - required skills
   - technologies
   - years of experience

5. If information is not present in the retrieved job descriptions,
   explicitly say that the available data does not establish it.

6. Distinguish clearly between:
   - what the job postings explicitly require
   - your interpretation of the market data

7. When analyzing skills, identify technologies and concepts that
   actually appear in the retrieved job descriptions.

8. Provide concise, structured answers.

For market analysis, use this structure:

ROLE
JOBS ANALYZED
COMPANIES
LOCATIONS
TOP REQUIRED SKILLS
TECHNOLOGIES
COMMON REQUIREMENTS
OBSERVATIONS
DATA LIMITATIONS

Do not provide salary estimates unless salary information was explicitly
present in the retrieved job data.
""",
    )

    print("\n5. Running Job Market Intelligence Agent...")

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Analyze the current market for Generative AI "
                        "and Applied AI Engineer jobs. "
                        "Focus on India if relevant, but use the available "
                        "live job data. "
                        "Tell me which skills and technologies are actually "
                        "required by the retrieved postings."
                    ),
                }
            ]
        }
    )

    print("\n" + "=" * 60)
    print("JOB MARKET INTELLIGENCE")
    print("=" * 60)
    print()

    response = result["messages"][-1].content

    print(response)

    print("\n" + "=" * 60)
    print("END")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())