from app.firebase_admin_box import firestore_bag
from fastapi import FastAPI

# I keep imports separate so it's obvious what my "API layer" is.
# Each router is a mini-module: it owns its endpoints and request/response models.
from app.api.chat import router as chat_router
from app.api.mood import router as mood_router
from app.api.report import router as report_router
from app.api.assessments import router as assessments_router
from app.api.ai import router as ai_router


def build_backend_app() -> FastAPI:
    # I created this FastAPI app object because this is the main entry point of my backend.
    # Uvicorn will look for "app" in app.main:app, so naming matters here.
    core_api = FastAPI(
        title="Nuvio Backend API",
        version="0.1.0",
    )

    # I register routers here so endpoints are organized by feature/module.
    # This makes it easier to demo and also easier to maintain later.
    core_api.include_router(chat_router)
    core_api.include_router(mood_router)
    core_api.include_router(report_router)
    core_api.include_router(assessments_router)
    core_api.include_router(ai_router)

    # I added this root endpoint because when I paste the base URL in a browser,
    # I don't want to see a 404 and panic. This is just my quick sanity check.
    @core_api.get("/")
    def home_ping():
        return {
            "ok": True,
            "note": "Backend is alive. I added this so the browser doesn't show 404.",
        }

    # I keep a /health endpoint because hosting platforms (Render etc.)
    # usually use something like this to check if the service is running.
    @core_api.get("/health")
    def health_probe():
        return {"ok": True, "service": "backend-api"}

    return core_api


# IMPORTANT:
# Uvicorn expects the variable name "app" when we run: uvicorn app.main:app
# So I expose the built FastAPI instance as "app" here.
app = build_backend_app()

@app.get("/firebase/ping")
def firebase_ping():
    # I use this endpoint to prove my backend can talk to Firestore using Admin SDK
    db = firestore_bag()

    # I write a tiny debug doc so I can confirm it appears in Firebase console
    ref = db.collection("_backend_smoke_tests").document("hello-from-berkay")
    ref.set(
        {
            "msg": "If you see this, my backend can write to Firestore ✅",
            "where": "codespaces",
        }
    )

    snap = ref.get()
    return {"ok": True, "wrote_doc": snap.to_dict()}
