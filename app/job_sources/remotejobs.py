import httpx
from datetime import datetime, timezone

from app.job_sources.models import Job


BASE_URL = "https://remotejobs.org/api/v1/jobs"


def normalize_timestamp(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(
            value,
            tz=timezone.utc,
        ).isoformat()

    return str(value)


def search_jobs(
    keyword: str | None = None,
    category: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Job]:
    params = {
        "limit": min(limit, 50),
        "offset": offset,
    }

    if keyword:
        params["q"] = keyword

    if category:
        params["category"] = category

    response = httpx.get(
        BASE_URL,
        params=params,
        timeout=15.0,
    )
    response.raise_for_status()

    data = response.json()
    jobs = []

    for item in data.get("data", []):
        job_id = item.get("id")

        if not job_id:
            continue

        company = item.get("company") or {}
        company_name = (
            company.get("name")
            if isinstance(company, dict)
            else str(company)
        )

        jobs.append(
            Job(
                id=f"remotejobs_{job_id}",
                company=company_name or "Unknown",
                title=item.get("title") or "Untitled role",
                location=item.get("location"),
                description=item.get("description"),
                url=item.get("apply_url") or item.get("url"),
                source="remotejobs",
                source_job_id=str(job_id),
                published_at=normalize_timestamp(item.get("posted_at")),
                updated_at=None,
            )
        )

    return jobs
