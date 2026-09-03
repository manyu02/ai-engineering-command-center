import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

from app.job_sources.greenhouse import (
    get_jobs,
    get_job_description as fetch_job_description,
)

mcp = FastMCP("job-market")


GREENHOUSE_COMPANIES = {
    "anthropic": {
        "board_token": "anthropic",
        "name": "Anthropic",
    },
}


def get_greenhouse_company(company: str):
    company_key = company.lower().strip()

    for key, config in GREENHOUSE_COMPANIES.items():
        if key in company_key or company_key in key:
            return config

    return None


def role_relevance_score(title: str, role: str) -> float:
    title_words = set(title.lower().replace("-", " ").split())
    role_words = {
        word
        for word in role.lower().replace("-", " ").split()
        if len(word) > 2 and word not in {"and", "the", "for"}
    }

    if not role_words:
        return 0.0

    generic_words = {
        "ai", "ml", "data", "engineer", "developer",
        "software", "senior", "junior", "lead"
    }

    meaningful_words = role_words - generic_words

    if not meaningful_words:
        return 1.0 if title_words & role_words else 0.0

    matches = len(title_words & meaningful_words)
    score = matches / len(meaningful_words)

    if role.lower().strip() == title.lower().strip():
        score = 1.0

    return round(min(score, 1.0), 2)


def role_matches(title: str, role: str) -> bool:
    return role_relevance_score(title, role) >= 0.5

@mcp.tool()
def search_jobs(
    role: str,
    location: str | None = None,
    seniority: str | None = None,
) -> list[dict]:
    """Search live Greenhouse jobs by role and optional location."""

    results = []

    for company_config in GREENHOUSE_COMPANIES.values():
        data = get_jobs(company_config["board_token"])

        for job in data.get("jobs", []):
            title = job.get("title", "")
            job_location = job.get("location", {}).get("name", "")

            role_match = role_matches(title, role)

            location_match = (
                location is None
                or location.lower() in job_location.lower()
            )

            seniority_match = (
                seniority is None
                or seniority.lower() in title.lower()
            )

            if role_match and location_match and seniority_match:
                results.append({
                    "job_id": f"greenhouse_{job['id']}",
                    "company": company_config["name"],
                    "title": title,
                    "relevance_score": role_relevance_score(title, role),
                    "location": job_location,
                    "url": job.get("absolute_url"),
                    "source": "greenhouse",
                })

    return results


@mcp.tool()
def get_job_description(job_id: str) -> dict:
    """Retrieve the full live job description using its job ID."""

    clean_job_id = str(job_id).replace("greenhouse_", "")

    for company_config in GREENHOUSE_COMPANIES.values():
        try:
            job = fetch_job_description(
                company_config["board_token"],
                clean_job_id,
                company_config["name"],
            )

            return job.model_dump()

        except Exception:
            continue

    return {"error": f"Job {job_id} not found"}


@mcp.tool()
def get_company_jobs(
    company: str,
    role: str | None = None,
) -> list[dict]:
    """Retrieve live jobs from a supported company."""

    company_config = get_greenhouse_company(company)

    if not company_config:
        return {
            "error": (
                f"Company '{company}' is not currently configured "
                "as a Greenhouse source."
            )
        }

    data = get_jobs(company_config["board_token"])

    results = []

    for job in data.get("jobs", []):
        title = job.get("title", "")
        location = job.get("location", {}).get("name", "")

        role_match = (
            role is None
            or role_matches(title, role)
        )

        if role_match:
            results.append({
                "job_id": f"greenhouse_{job['id']}",
                "company": company_config["name"],
                "title": title,
                "location": location,
                "url": job.get("absolute_url"),
                "source": "greenhouse",
            })

    return results


@mcp.tool()
def get_market_snapshot(
    role: str,
    location: str | None = None,
    max_jobs: int = 10,
) -> dict:
    jobs = search_jobs(role=role, location=location)
    jobs = jobs[:max_jobs]

    enriched_jobs = []

    for job in jobs:
        description = get_job_description(job["job_id"])
        enriched_jobs.append({
            "job": job,
            "description": description,
        })

    ranked_jobs = sorted(
        enriched_jobs,
        key=lambda item: item["job"].get("relevance_score", 0),
        reverse=True,
    )

    companies = [
        item["job"].get("company")
        for item in ranked_jobs
        if item["job"].get("company")
    ]

    locations = [
        item["job"].get("location")
        for item in ranked_jobs
        if item["job"].get("location")
    ]

    scores = [
        item["job"].get("relevance_score", 0)
        for item in ranked_jobs
    ]

    return {
        "role": role,
        "location": location,
        "jobs_analyzed": len(ranked_jobs),
        "jobs": ranked_jobs,
        "market_stats": {
            "companies": sorted(set(companies)),
            "locations": sorted(set(locations)),
            "average_relevance_score": round(
                sum(scores) / len(scores), 2
            ) if scores else 0.0,
        },
        "source": "live_greenhouse",
        "instruction": (
            "Use only the supplied job data when making factual claims "
            "about this market. Do not invent salaries, companies, "
            "requirements, or job details."
        ),
    }

if __name__ == "__main__":
    mcp.run()