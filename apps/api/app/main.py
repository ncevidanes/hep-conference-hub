from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import Base, engine
from app.api import events, newsletter, admin
import app.models.domain  # noqa

Base.metadata.create_all(bind=engine)
app = FastAPI(title="HEP Conference Hub API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(events.router, prefix="/api/v1")
app.include_router(newsletter.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
