from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, events, newsletter
from app.core.config import settings
from app.services.bootstrap import initialize_database
import app.models.domain  # noqa: F401

initialize_database(seed_if_empty=settings.seed_on_startup)

app = FastAPI(title="HEP Conference Hub API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(events.router, prefix="/api/v1")
app.include_router(newsletter.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
