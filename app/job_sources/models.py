from pydantic import BaseModel
from typing import Optional


class Job(BaseModel):
    id: str
    company: str
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: str
    source_job_id: str
    published_at: Optional[str] = None
    updated_at: Optional[str] = None