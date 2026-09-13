import httpx
from app.job_sources.models import Job

BASE_URL = "https://jobicy.com/api/v2/remote-jobs"


def search_jobs(
    keyword: str | None = None,
    count: int = 200,
    geo: str | None = None,
    industry: str | None = None,
    tag: str | None = None,
) -> list[Job]:
    params = {"count": min(count, 200)}

    if geo:
        params["geo"] = geo

    if industry:
        params["industry"] = industry

    if tag:
        params["tag"] = tag

    response = httpx.get(BASE_URL, params=params, timeout=20.0)
    response.raise_for_status()

    data = response.json()

    jobs = []

    for item in data.get("jobs", []):
        job_id = item.get("id")

        if not job_id:
            continue

        jobs.append(
            Job(
                id=f"jobicy_{job_id}",
                company=item.get("companyName") or "Unknown",
                title=item.get("jobTitle") or "Untitled role",
                location=item.get("jobGeo"),
                description=item.get("jobDescription"),
                url=item.get("url"),
                source="jobicy",
                source_job_id=str(job_id),
                published_at=item.get("pubDate"),
                updated_at=None,
            )
        )

    return jobs[:count]