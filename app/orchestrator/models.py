from pydantic import BaseModel, Field


class SkillGapItem(BaseModel):

    skill: str

    current_level: str

    required_level: str

    gap: str

    priority: str


class SkillGapResult(BaseModel):

    summary: str

    gaps: list[SkillGapItem] = Field(default_factory=list)


class RoadmapWeek(BaseModel):

    week: int

    focus: str

    topics: list[str] = Field(default_factory=list)

    skills: list[str] = Field(default_factory=list)

    projects: list[str] = Field(default_factory=list)

    resources: list[str] = Field(default_factory=list)

    milestones: list[str] = Field(default_factory=list)

    deliverables: list[str] = Field(default_factory=list)


class RoadmapResult(BaseModel):

    strategy: str

    weeks: list[RoadmapWeek] = Field(default_factory=list)