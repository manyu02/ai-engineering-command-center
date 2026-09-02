from pydantic import BaseModel, Field
from typing import List


class UserProfile(BaseModel):
    role: str
    specialization: str
    target_companies: List[str] = Field(default_factory=list)
    preparation_days: int = Field(gt=0)
    current_knowledge: List[str] = Field(default_factory=list)