"""
SwiftJob API - AI-powered job hunt co-pilot backend service.
"""

import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==== Settings ==== #


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    OPENAI_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    LIPSYNC_API_KEY: str = ""
    SENDGRID_API_KEY: str = ""
    WORKATO_API_KEY: str = ""
    WORKATO_ACCOUNT_ID: str = ""
    JOB_API_KEY: str = ""
    JOB_API_ENDPOINT: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Singleton dependency for application settings."""
    return Settings()


# ==== Schemas ==== #


class UserPreferences(BaseModel):
    """User job search preferences."""

    desired_roles: list[str]
    locations: list[str]
    min_salary: int | None = None
    job_types: list[str] | None = None


class JobPosting(BaseModel):
    """Job posting information."""

    id: str
    title: str
    company: str
    location: str
    source: str
    url: HttpUrl | str
    description: str


class ApplicationCreateRequest(BaseModel):
    """Request to create a new job application."""

    job: JobPosting
    base_resume_text: str
    user_preferences: UserPreferences


class Application(BaseModel):
    """Job application record."""

    id: str
    job: JobPosting
    status: Literal["draft", "submitted", "interview", "offer", "rejected"]
    created_at: datetime


class InterviewPrepRequest(BaseModel):
    """Request for interview preparation content."""

    application_id: str
    focus_areas: list[str] | None = None


class InterviewPrepResponse(BaseModel):
    """Interview preparation content."""

    questions: list[str]
    suggested_answers: list[str]


# ==== Service layer placeholders ==== #


class LLMService:
    """Service for LLM-powered content generation."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def generate_tailored_resume(
        self, req: ApplicationCreateRequest
    ) -> str:
        """
        Generate a tailored resume based on job posting and user preferences.

        TODO: Implement OpenAI API call to tailor resume text.
        """
        # TODO: Call OpenAI API with job description and base resume
        # TODO: Use settings.OPENAI_API_KEY
        return req.base_resume_text

    async def generate_interview_prep(
        self, req: InterviewPrepRequest
    ) -> InterviewPrepResponse:
        """
        Generate interview preparation questions and suggested answers.

        TODO: Implement OpenAI API call to generate interview prep content.
        """
        # TODO: Call OpenAI API with application details and focus areas
        # TODO: Use settings.OPENAI_API_KEY
        return InterviewPrepResponse(
            questions=["Sample question 1", "Sample question 2"],
            suggested_answers=["Sample answer 1", "Sample answer 2"],
        )


class JobSourceService:
    """Service for searching job postings."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def search_jobs(self, prefs: UserPreferences) -> list[JobPosting]:
        """
        Search for jobs based on user preferences.

        TODO: Implement job search (own DB or external API).
        """
        # TODO: Query Supabase or external job API
        # TODO: Use settings.JOB_API_KEY and settings.JOB_API_ENDPOINT
        # TODO: Filter by prefs.desired_roles, prefs.locations, etc.
        return []


class ApplicationService:
    """Service for managing job applications."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._applications: dict[str, Application] = {}

    async def create_application(
        self, job: JobPosting, status: str = "draft"
    ) -> Application:
        """Create a new application record."""
        import uuid

        application_id = str(uuid.uuid4())
        application = Application(
            id=application_id,
            job=job,
            status=status,
            created_at=datetime.utcnow(),
        )
        self._applications[application_id] = application
        return application

    async def list_applications(self) -> list[Application]:
        """List all applications."""
        return list(self._applications.values())

    async def get_application(self, application_id: str) -> Application | None:
        """Get a single application by ID."""
        return self._applications.get(application_id)


class NotificationService:
    """Service for sending notifications."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def send_status_email(self, application: Application) -> None:
        """
        Send email notification about application status.

        TODO: Implement SendGrid email sending.
        """
        # TODO: Use SendGrid API to send email
        # TODO: Use settings.SENDGRID_API_KEY
        pass


class WorkatoClient:
    """Client for triggering Workato/MCP workflows."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = httpx.AsyncClient()

    async def trigger_job_apply(self, application: Application) -> None:
        """
        Trigger Workato workflow to apply for a job.

        TODO: Implement Workato API call to trigger job application workflow.
        """
        # TODO: Call Workato API to trigger workflow
        # TODO: Use settings.WORKATO_API_KEY and settings.WORKATO_ACCOUNT_ID
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()


# ==== Dependency providers ==== #


_llm_service: LLMService | None = None
_job_source_service: JobSourceService | None = None
_application_service: ApplicationService | None = None
_notification_service: NotificationService | None = None
_workato_client: WorkatoClient | None = None


def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMService:
    """Dependency provider for LLMService."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(settings)
    return _llm_service


def get_job_source_service(
    settings: Settings = Depends(get_settings),
) -> JobSourceService:
    """Dependency provider for JobSourceService."""
    global _job_source_service
    if _job_source_service is None:
        _job_source_service = JobSourceService(settings)
    return _job_source_service


def get_application_service(
    settings: Settings = Depends(get_settings),
) -> ApplicationService:
    """Dependency provider for ApplicationService."""
    global _application_service
    if _application_service is None:
        _application_service = ApplicationService(settings)
    return _application_service


def get_notification_service(
    settings: Settings = Depends(get_settings),
) -> NotificationService:
    """Dependency provider for NotificationService."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService(settings)
    return _notification_service


def get_workato_client(
    settings: Settings = Depends(get_settings),
) -> WorkatoClient:
    """Dependency provider for WorkatoClient."""
    global _workato_client
    if _workato_client is None:
        _workato_client = WorkatoClient(settings)
    return _workato_client


# ==== Router definitions ==== #


router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)) -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "llm_configured": bool(settings.OPENAI_API_KEY),
    }


@router.post("/preferences/test-search")
async def test_job_search(
    preferences: UserPreferences,
    job_service: JobSourceService = Depends(get_job_source_service),
) -> list[JobPosting]:
    """
    Test endpoint to search for jobs based on preferences.

    TODO: Replace mock data with real job search implementation.
    """
    # TODO: Replace with real job search
    # For now, return mock jobs
    mock_jobs = [
        JobPosting(
            id="mock-1",
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            source="mock",
            url="https://example.com/job/1",
            description="Mock job description",
        )
    ]
    return mock_jobs


@router.post("/applications")
async def create_application(
    req: ApplicationCreateRequest,
    llm_service: LLMService = Depends(get_llm_service),
    app_service: ApplicationService = Depends(get_application_service),
    workato_client: WorkatoClient = Depends(get_workato_client),
    notification_service: NotificationService = Depends(
        get_notification_service
    ),
) -> Application:
    """
    Create a new job application.

    Flow:
    1. Generate tailored resume using LLM
    2. Create application record (status="draft")
    3. Trigger Workato workflow to apply
    4. Update status to "submitted"
    5. Send notification email (async)
    """
    # Step 1: Generate tailored resume
    tailored_resume = await llm_service.generate_tailored_resume(req)

    # Step 2: Create application record
    application = await app_service.create_application(
        job=req.job, status="draft"
    )

    # Step 3: Trigger Workato workflow
    await workato_client.trigger_job_apply(application)

    # Step 4: Update status to submitted
    application.status = "submitted"
    app_service._applications[application.id] = application

    # Step 5: Send notification asynchronously (fire-and-forget)
    asyncio.create_task(notification_service.send_status_email(application))

    return application


@router.get("/applications")
async def list_applications(
    app_service: ApplicationService = Depends(get_application_service),
) -> list[Application]:
    """List all job applications."""
    return await app_service.list_applications()


@router.get("/applications/{application_id}")
async def get_application(
    application_id: str,
    app_service: ApplicationService = Depends(get_application_service),
) -> Application:
    """Get a single application by ID."""
    application = await app_service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post("/applications/{application_id}/interview-prep")
async def generate_interview_prep(
    application_id: str,
    req: InterviewPrepRequest,
    llm_service: LLMService = Depends(get_llm_service),
    app_service: ApplicationService = Depends(get_application_service),
) -> InterviewPrepResponse:
    """
    Generate interview preparation content for an application.

    TODO: Enhance with ElevenLabs/LipSync integration for video prep.
    """
    # Verify application exists
    application = await app_service.get_application(application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    # Generate interview prep content
    prep_response = await llm_service.generate_interview_prep(req)

    return prep_response


# ==== App creation ==== #


app = FastAPI(title="SwiftJob API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

