import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from prometheus_fastapi_instrumentator import Instrumentator

from app.middleware import RequestLoggingMiddleware
from app.profile import UserProfile
from app.orchestrator.agent import JobMarketAgent
from app.orchestrator.interview import InterviewAgent
from app.orchestrator.interview_evaluation import InterviewEvaluator
from app.orchestrator.roadmap import RoadmapGenerator
from app.orchestrator.skill_gap import SkillGapAnalyzer
from app.orchestrator.candidate_intelligence import CandidateIntelligence
from app.orchestrator.adaptive_learning import AdaptiveLearning
from app.orchestrator.rag import RAGEngine
from app.profile_store import load_profile, save_profile


latest_adaptive_learning = None

agent = JobMarketAgent()
interview_agent = InterviewAgent(agent.llm)
interview_evaluator = InterviewEvaluator(agent.llm)
skill_gap_analyzer = SkillGapAnalyzer()
roadmap_generator = RoadmapGenerator()
candidate_intelligence = CandidateIntelligence()
adaptive_learning_engine = AdaptiveLearning()
rag_engine = RAGEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="AI Engineering Command Center",
    version="1.0.0",
    lifespan=lifespan,
)


resource = Resource.create(
    {
        "service.name": "ai-command-center",
        "service.version": "1.0.0",
    }
)

tracer_provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://127.0.0.1:4317",
    insecure=True,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

trace.set_tracer_provider(tracer_provider)

FastAPIInstrumentor.instrument_app(app)

app.add_middleware(RequestLoggingMiddleware)

Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
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


class InterviewQuestionRequest(BaseModel):
    role: str = Field(min_length=2)
    specialization: str | None = None
    history: list[dict] = Field(default_factory=list)


class InterviewEvaluationRequest(BaseModel):
    role: str = Field(min_length=2)
    question: str = Field(min_length=5)
    answer: str = Field(min_length=1)


class AdaptiveLearningRequest(BaseModel):
    evaluation: dict


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
        total_start = time.perf_counter()

        market_start = time.perf_counter()

        market = await agent.analyze(
            role=request.role,
            location=request.location,
            specialization=request.specialization,
        )

        print(
            f"[TIMING] market.analyze: "
            f"{time.perf_counter() - market_start:.2f}s"
        )

        skill_start = time.perf_counter()

        skill_gap = await skill_gap_analyzer.analyze(
            current_knowledge=request.current_knowledge,
            market_analysis=market["analysis"],
        )

        print(
            f"[TIMING] skill_gap.analyze: "
            f"{time.perf_counter() - skill_start:.2f}s"
        )

        candidate = candidate_intelligence.analyze(
            current_knowledge=request.current_knowledge,
            jobs=market.get("jobs", []),
        )

        rag_context = rag_engine.format_context(
            f"{request.role} {request.specialization or ''}"
        )

        roadmap_start = time.perf_counter()

        roadmap = await roadmap_generator.generate(
            role=request.role,
            specialization=request.specialization,
            preparation_days=request.preparation_days,
            current_knowledge=request.current_knowledge,
            skill_gap=skill_gap,
            adaptive_learning=latest_adaptive_learning,
        )

        print(
            f"[TIMING] roadmap.generate: "
            f"{time.perf_counter() - roadmap_start:.2f}s"
        )

        print(
            f"[TIMING] command_center.total: "
            f"{time.perf_counter() - total_start:.2f}s"
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
            "candidate_intelligence": candidate,
            "rag_context": rag_context,
            "roadmap": roadmap,
            "adaptive_learning": latest_adaptive_learning,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Command Center analysis failed: {str(exc)}",
        )


@app.post("/api/v1/interview/question")
async def interview_question(request: InterviewQuestionRequest):
    try:
        return await interview_agent.generate_question(
            role=request.role,
            specialization=request.specialization,
            history=request.history,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Interview question generation failed: {str(exc)}",
        )


@app.post("/api/v1/interview/evaluate")
async def interview_evaluate(request: InterviewEvaluationRequest):
    global latest_adaptive_learning

    try:
        evaluation = await interview_evaluator.evaluate(
            role=request.role,
            question=request.question,
            answer=request.answer,
        )

        latest_adaptive_learning = evaluation.get(
            "adaptive_learning"
        )

        return evaluation

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Interview evaluation failed: {str(exc)}",
        )


@app.post("/api/v1/learning/adjust")
async def learning_adjust(request: AdaptiveLearningRequest):
    try:
        return adaptive_learning_engine.generate_adjustments(
            request.evaluation
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Adaptive learning adjustment failed: {str(exc)}",
        )


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


frontend_path = "app/static/frontend/dist"

try:
    app.mount(
        "/",
        StaticFiles(
            directory=frontend_path,
            html=True,
        ),
        name="frontend",
    )
except RuntimeError:
    pass