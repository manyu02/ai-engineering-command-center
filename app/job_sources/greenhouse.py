import httpx
from html import unescape
import re
from app.job_sources.models import Job


BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

def clean_html(html_content: str | None) -> str | None:
    if not html_content:
        return None

    text = unescape(html_content)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()
def get_jobs(board_token: str, include_content: bool = False) -> dict:
    url = f"{BASE_URL}/{board_token}/jobs"

    response = httpx.get(
        url,
        params={"content": str(include_content).lower()},
        timeout=20.0,
    )

    response.raise_for_status()

    return response.json()


def normalize_job(job_data: dict, company: str) -> Job:
    return Job(
        id=f"greenhouse_{job_data['id']}",
        company=company,
        title=job_data["title"],
        location=job_data.get("location", {}).get("name"),
        description=clean_html(job_data.get("content")),
        url=job_data.get("absolute_url"),
        source="greenhouse",
        source_job_id=str(job_data["id"]),
        published_at=job_data.get("first_published"),
        updated_at=job_data.get("updated_at"),

    )
def get_job_description(
    board_token: str,
    job_id: str,
    company: str,
) -> Job:
    url = f"{BASE_URL}/{board_token}/jobs/{job_id}"

    response = httpx.get(
        url,
        timeout=20.0,
    )

    response.raise_for_status()

    job_data = response.json()

    return normalize_job(job_data, company)

if __name__ == "__main__":
    job = get_job_description(
        "anthropic",
        "4461450008",
        "Anthropic",
    )

    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Location: {job.location}")
    print(f"URL: {job.url}")
    print(f"Source: {job.source}")
    print(f"Source Job ID: {job.source_job_id}")

    print("\nDESCRIPTION:\n")
    print(job.description[:3000])