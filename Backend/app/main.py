from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.resume import router as resume_router
from api.v1.job_description import router as jd_router
from api.v1.interview import router as interview_router
from api.v1.voice import router as voice_router

app = FastAPI(
    title="AI Mock Interviewer API",
    description="Enterprise Multi-Agent Mock Interview Backend Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(resume_router, prefix="/api/v1")
app.include_router(jd_router, prefix="/api/v1")
app.include_router(interview_router, prefix="/api/v1")
app.include_router(voice_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Interviewer Backend",
        "version": "1.0.0",
        "endpoints": {
            "resume_upload": "POST /api/v1/resume/upload",
            "resume_analyze": "POST /api/v1/resume/analyze",
            "interview_plan": "POST /api/v1/interview/plan",
            "interview_start": "POST /api/v1/interview/start",
            "interview_match": "POST /api/v1/interview/match",
            "voice_transcribe": "POST /api/v1/voice/transcribe",
            "voice_synthesize": "POST /api/v1/voice/synthesize",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
