from collections import defaultdict
import re

from app.job_sources.models import Job
from app.job_sources import greenhouse, himalayas, remotejobs, jobicy


SENIORITY_WORDS = {
    "senior",
    "junior",
    "lead",
    "principal",
    "staff",
    "associate",
}


def _tokens(text: str | None) -> set[str]:
    if not text:
        return set()

    return {
        token.strip(".,:;()[]{}'\"")
        for token in text.lower().replace("-", " ").split()
        if len(token.strip(".,:;()[]{}'\"")) > 1
    }


def _role_variants(role: str) -> list[str]:
    role = " ".join(role.lower().strip().split())

    if not role:
        return []

    variants = [role]

    parts = [
        part.strip()
        for part in re.split(r"\s+(?:and|&)\s+|/", role)
        if part.strip()
    ]

    if len(parts) > 1:
        final_word = role.split()[-1]

        for part in parts:
            if part.split()[-1] != final_word:
                variants.append(f"{part} {final_word}")
            else:
                variants.append(part)

    result = []

    for variant in variants:
        if variant not in result:
            result.append(variant)

    return result


def _single_role_score(job: Job, role: str) -> float:
    role_tokens = _tokens(role)
    title_tokens = _tokens(job.title)
    description_tokens = _tokens(job.description)

    if not role_tokens:
        return 0.0

    meaningful_tokens = role_tokens - SENIORITY_WORDS

    if not meaningful_tokens:
        meaningful_tokens = role_tokens

    role_phrase = " ".join(
        token
        for token in role.lower().strip().split()
        if token not in SENIORITY_WORDS
    )

    title_text = " ".join(job.title.lower().split())

    if role_phrase and role_phrase in title_text:
        return 1.0

    title_matches = len(meaningful_tokens & title_tokens)
    description_matches = len(
        meaningful_tokens & description_tokens
    )

    if len(meaningful_tokens) == 1:
        return round(
            min(
                title_matches * 0.6
                + description_matches * 0.4,
                1.0,
            ),
            3,
        )

    title_score = title_matches / len(meaningful_tokens)
    description_score = description_matches / len(meaningful_tokens)

    if title_matches == len(meaningful_tokens):
        return 1.0

    if title_matches == 0:
        return round(description_score * 0.3, 3)

    return round(
        min(
            title_score * 0.7
            + description_score * 0.3,
            1.0,
        ),
        3,
    )

def _role_score(job: Job, role: str) -> float:
    variants = _role_variants(role)

    if not variants:
        return 0.0

    return max(
        _single_role_score(job, variant)
        for variant in variants
    )


def _specialization_score(
    job: Job,
    specialization: str | None,
) -> float:
    if not specialization:
        return 0.0

    specialization_tokens = _tokens(specialization)

    if not specialization_tokens:
        return 0.0

    meaningful_tokens = {
        token
        for token in specialization_tokens
        if token not in {"ai", "ml", "and", "or"}
    }

    if not meaningful_tokens:
        meaningful_tokens = specialization_tokens

    title_tokens = _tokens(job.title)
    description_tokens = _tokens(job.description)

    title_matches = len(
        meaningful_tokens & title_tokens
    )

    description_matches = len(
        meaningful_tokens & description_tokens
    )

    if title_matches == len(meaningful_tokens):
        return 1.0

    if title_matches > 0:
        return 0.7

    if description_matches >= max(1, len(meaningful_tokens) // 2):
        return 0.5

    if description_matches > 0:
        return 0.2

    return 0.0

def _location_score(
    job_location: str | None,
    requested_location: str | None,
) -> float:
    if not requested_location:
        return 0.5

    if not job_location:
        return 0.0

    requested = requested_location.lower().strip()
    actual = job_location.lower().strip()

    if requested in actual:
        return 1.0

    if "remote" in actual:
        return 0.7

    if any(
        term in actual
        for term in {
            "worldwide",
            "anywhere",
            "global",
        }
    ):
        return 0.7

    return 0.0


def _rank_job(
    job: Job,
    role: str,
    specialization: str | None,
    location: str | None,
) -> dict:
    role_score = _role_score(job, role)
    specialization_score = _specialization_score(
        job,
        specialization,
    )
    location_score = _location_score(
        job.location,
        location,
    )

    final_score = round(
        role_score * 0.60
        + specialization_score * 0.25
        + location_score * 0.15,
        3,
    )

    return {
        "job": job,
        "score": final_score,
        "role_score": role_score,
        "specialization_score": specialization_score,
        "location_score": location_score,
    }


def _deduplicate(jobs: list[Job]) -> list[Job]:
    seen: dict[str, Job] = {}

    for job in jobs:
        key = (
            job.url.lower().strip()
            if job.url
            else f"{job.company.lower()}::{job.title.lower()}::{job.location}"
        )

        if key not in seen:
            seen[key] = job

    return list(seen.values())


def search_jobs(
    role: str,
    location: str | None = None,
    specialization: str | None = None,
    max_jobs: int = 10,
) -> dict:
    candidates: list[Job] = []
    source_counts = defaultdict(int)

    role_queries = _role_variants(role)

    sources = [
        (
            "himalayas",
            lambda: [
                job
                for query in role_queries
                for job in himalayas.search_jobs(
                    keyword=query,
                    limit=20,
                )
            ],
        ),
        (
            "remotejobs",
            lambda: [
                job
                for query in role_queries
                for job in remotejobs.search_jobs(
                    keyword=query,
                    limit=50,
                )
            ],
        ),
        (
            "jobicy",
            lambda: jobicy.search_jobs(
                count=200,
            ),
        ),
        (
            "greenhouse",
            lambda: [
                greenhouse.normalize_job(job, "Anthropic")
                for job in greenhouse.get_jobs("anthropic").get("jobs", [])
            ],
        ),
    ]

    for source_name, loader in sources:
        try:
            jobs = loader()

            for job in jobs:
                candidates.append(job)
                source_counts[source_name] += 1

        except Exception:
            continue

    candidates = _deduplicate(candidates)

    ranked = []

    for job in candidates:
        ranking = _rank_job(
            job,
            role,
            specialization,
            location,
        )

        if ranking["role_score"] < 0.4:
            continue

        ranked.append(
            {
                "job": job,
                "relevance_score": ranking["score"],
                "role_score": ranking["role_score"],
                "specialization_score": ranking["specialization_score"],
                "location_score": ranking["location_score"],
            }
        )

    ranked.sort(
        key=lambda item: item["relevance_score"],
        reverse=True,
    )

    selected = ranked[:max_jobs]

    return {
        "role": role,
        "specialization": specialization,
        "location": location,
        "jobs_found": len(selected),
        "jobs": selected,
        "candidates_considered": len(candidates),
        "source_counts": dict(source_counts),
    }