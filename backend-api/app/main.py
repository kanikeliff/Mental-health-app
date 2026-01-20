from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# I keep imports separate so it's obvious what my "API layer" is.
from app.api.chat import router as chat_router
from app.api.mood import router as mood_router
from app.api.report import router as report_router
from app.api.assessments import router as assessments_router


def build_nuvio_app() -> FastAPI:
    # I wrap app creation into a function so tests can import it easily.
    api = FastAPI(
        title="Nuvio Backend API",
        version="0.1.0",
    )

    # I enable CORS mainly for quick web testing.
    # iOS usually doesn't need this, but it never hurts for demo environments.
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # I register routers here, so endpoints are organized by module.
    api.include_router(chat_router)
    api.include_router(mood_router)
    api.include_router(report_router)
    api.include_router(assessments_router)

    @api.get("/health")
    def health():
        # I keep this endpoint public for Render health checks.
        return {"ok": True, "service": "nuvio-backend"}

    return api


app = build_nuvio_app()
