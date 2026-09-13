import httpx
from datetime import datetime, timezone

from app.job_sources.models import Job


BASE_URL = "https://himalayas.app/jobs/api/search"


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
    keyword: str,
    country: str | None = None,
    worldwide: bool = True,
    limit: int = 20,
) -> list[Job]:
    params = {
        "q": keyword,
        "limit": limit,
    }

    if country:
        params["country"] = country

    if worldwide:
        params["worldwide"] = "true"

    response = httpx.get(
        BASE_URL,
        params=params,
        timeout=15.0,
    )
    response.raise_for_status()

    data = response.json()
    jobs = []

    for item in data.get("jobs", []):
        job_id = item.get("guid") or item.get("applicationLink")

        if not job_id:
            continue

        location = None

        restrictions = item.get("locationRestrictions") or []
        if restrictions:
            location = ", ".join(str(value) for value in restrictions)

        jobs.append(
            Job(
                id=f"himalayas_{job_id}",
                company=item.get("companyName") or "Unknown",
                title=item.get("title") or "Untitled role",
                location=location,
                description=item.get("description") or item.get("excerpt"),
                url=item.get("applicationLink") or item.get("guid"),
                source="himalayas",
                source_job_id=str(job_id),
                published_at=normalize_timestamp(item.get("pubDate")),
                updated_at=normalize_timestamp(item.get("expiryDate")),
            )
        )

    return jobs[:limit]
