from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.profile import UserProfile
from app.profile_store import load_profile, save_profile
from app.orchestrator.agent import JobMarketAgent
from app.orchestrator.skill_gap import SkillGapAnalyzer
from app.orchestrator.roadmap import RoadmapGenerator

agent = JobMarketAgent()
skill_gap_analyzer = SkillGapAnalyzer()
roadmap_generator = RoadmapGenerator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.initialize()
    yield


app = FastAPI(
    title="AI Engineering Command Center",
    description="AI-powered career intelligence platform",
    version="0.3.0",
    lifespan=lifespan,
)


class CommandCenterRequest(BaseModel):
    role: str = Field(min_length=2)
    location: str | None = None
    specialization: str | None = None
    preparation_days: int = Field(gt=0)
    current_knowledge: list[str] = Field(default_factory=list)


class MarketAnalysisRequest(BaseModel):
    role: str = Field(min_length=2)
    location: str | None = None
    specialization: str | None = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-engineering-command-center",
    }

@app.post("/api/v1/profile")
async def create_profile(profile: UserProfile):

    save_profile(profile)

    return {
        "status": "created",
        "profile": profile.model_dump(),
    }


@app.get("/api/v1/profile")
async def get_profile():

    profile = load_profile()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return profile.model_dump()

@app.post("/api/v1/plan/generate")
async def generate_plan():

    profile = load_profile()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Create a profile first.",
        )

    try:
        return await agent.generate_plan(profile)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Plan generation failed: {str(exc)}",
        )
    
@app.post("/api/v1/market/analyze")
async def analyze_market(request: MarketAnalysisRequest):

    try:
        return await agent.analyze(
            role=request.role,
            location=request.location,
            specialization=request.specialization,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Market analysis failed: {str(exc)}",
        )


@app.post("/api/v1/command-center/analyze")
async def command_center(request: CommandCenterRequest):

    try:
        market = await agent.analyze(
            role=request.role,
            location=request.location,
            specialization=request.specialization,
        )

        skill_gap = await skill_gap_analyzer.analyze(
            current_knowledge=request.current_knowledge,
            market_analysis=market["analysis"],
        )

        roadmap = await roadmap_generator.generate(
            role=request.role,
            specialization=request.specialization,
            preparation_days=request.preparation_days,
            current_knowledge=request.current_knowledge,
            skill_gap=skill_gap,
        )

        return {
            "profile": {
                "role": request.role,
                "location": request.location,
                "specialization": request.specialization,
                "preparation_days": request.preparation_days,
                "current_knowledge": request.current_knowledge,
            },
            "market": market,
            "skill_gap": skill_gap,
            "roadmap": roadmap,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Command center analysis failed: {str(exc)}",
        )
app.mount(
    "/",
    StaticFiles(directory="app/static", html=True),
    name="static",
)