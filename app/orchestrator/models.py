from pydantic import BaseModel, Field


class SkillRequirement(BaseModel):
    skill: str
    frequency: int = Field(ge=1)
    evidence: list[str] = Field(default_factory=list)


class MarketAnalysis(BaseModel):
    role: str
    location: str | None
    jobs_analyzed: int
    companies: list[str]
    skills: list[SkillRequirement]
    technologies: list[SkillRequirement]
    observations: list[str]
    limitations: list[str]


class SkillGap(BaseModel):
    skill: str
    importance: int = Field(ge=1, le=10)
    status: str
    reason: str


class SkillGapAnalysis(BaseModel):
    strengths: list[str]
    gaps: list[SkillGap]
    priorities: list[str]