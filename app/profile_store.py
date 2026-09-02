import json
from pathlib import Path

from app.profile import UserProfile


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROFILE_FILE = DATA_DIR / "user_profile.json"


def save_profile(profile: UserProfile) -> UserProfile:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    PROFILE_FILE.write_text(
        json.dumps(
            profile.model_dump(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return profile


def load_profile() -> UserProfile | None:
    if not PROFILE_FILE.exists():
        return None

    data = json.loads(
        PROFILE_FILE.read_text(encoding="utf-8")
    )

    return UserProfile.model_validate(data)