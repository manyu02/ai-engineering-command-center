import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.profile import UserProfile


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROFILE_FILE = DATA_DIR / "user_profile.json"


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
