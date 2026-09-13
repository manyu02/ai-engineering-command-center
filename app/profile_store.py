import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.profile import UserProfile


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROFILE_FILE = DATA_DIR / "user_profile.json"
ROADMAP_FILE = DATA_DIR / "roadmap.json"


def save_profile(profile: UserProfile) -> UserProfile:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    data = json.dumps(
        profile.model_dump(),
        indent=2,
        ensure_ascii=False,
    )

    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=DATA_DIR,
        delete=False,
    ) as temp_file:
        temp_file.write(data)
        temp_path = Path(temp_file.name)

    os.replace(temp_path, PROFILE_FILE)

    return profile


def load_profile() -> UserProfile | None:
    if not PROFILE_FILE.exists():
        return None

    try:
        data = json.loads(
            PROFILE_FILE.read_text(encoding="utf-8")
        )
        return UserProfile.model_validate(data)

    except (json.JSONDecodeError, ValueError):
        return None


def roadmap_fingerprint(profile: UserProfile) -> str:
    payload = {
        "role": profile.role.strip().lower(),
        "specialization": profile.specialization.strip().lower(),
        "current_knowledge": sorted(
            topic.strip().lower()
            for topic in profile.current_knowledge
            if topic.strip()
        ),
        "preparation_days": int(profile.preparation_days),
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def save_roadmap(
    fingerprint: str,
    roadmap: dict,
) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "fingerprint": fingerprint,
        "roadmap": roadmap,
    }

    data = json.dumps(
        payload,
        indent=2,
        ensure_ascii=False,
    )

    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=DATA_DIR,
        delete=False,
    ) as temp_file:
        temp_file.write(data)
        temp_path = Path(temp_file.name)

    os.replace(temp_path, ROADMAP_FILE)

    return roadmap


def load_roadmap(
    fingerprint: str,
) -> dict | None:
    if not ROADMAP_FILE.exists():
        return None

    try:
        data = json.loads(
            ROADMAP_FILE.read_text(encoding="utf-8")
        )

        if data.get("fingerprint") != fingerprint:
            return None

        roadmap = data.get("roadmap")

        if not isinstance(roadmap, dict):
            return None

        return roadmap

    except (json.JSONDecodeError, ValueError):
        return None

