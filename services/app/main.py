from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import ExperimentContextMiddleware
from app.api.routes import (
    admin, consent, experiments, feedback, hackathons, internships, notifications,
    profile, scholarships, workflow, search_api, documents_api, connectors, chat
)
from app.api.routes import eval as eval_routes
from app.config import get_settings
from app.db.session import init_db
from app.ingestion.pipeline import run_ingestion

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Seed hackathon data on startup (dummy connectors run instantly; live
    # scrapers are async-wrapped and run in a thread so startup isn't blocked).
    import threading
    def _seed_hackathons():
        try:
            from app.db.session import SessionLocal
            from app.ingestion.hackathon_pipeline import run_hackathon_ingestion
            db = SessionLocal()
            try:
                stats = run_hackathon_ingestion(db)
                import logging
                logging.getLogger(__name__).info(
                    f"Hackathon seed: inserted={stats['inserted']} "
                    f"updated={stats['updated']} errors={stats['errors']}"
                )
            finally:
                db.close()
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Hackathon seed failed: {exc}")

    t = threading.Thread(target=_seed_hackathons, daemon=True)
    t.start()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Experiment context middleware for A/B testing
# This automatically assigns users to experiments and tracks variants in request state
app.add_middleware(ExperimentContextMiddleware)

app.include_router(scholarships.router, prefix="/api/v1")
app.include_router(internships.router, prefix="/api/v1")
app.include_router(hackathons.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(consent.router, prefix="/api/v1")
app.include_router(workflow.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(experiments.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(search_api.router)
app.include_router(documents_api.router)
app.include_router(connectors.router)
app.include_router(chat.router, prefix="/api/v1")
app.include_router(eval_routes.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "mvp_agent": "scholarship", "version": "1.0.0"}
