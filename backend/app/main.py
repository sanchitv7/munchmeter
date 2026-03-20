from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db
from app.routers import transcribe, extract, nutrition, meals
from app.services.ifct import initialize as _ifct_initialize


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ifct_initialize()
    await init_db()
    yield


app = FastAPI(
    title="MunchMeter API",
    description="Voice-first calorie tracker",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe.router, prefix="/api", tags=["transcribe"])
app.include_router(extract.router, prefix="/api", tags=["extract"])
app.include_router(nutrition.router, prefix="/api", tags=["nutrition"])
app.include_router(meals.router, prefix="/api", tags=["meals"])


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve frontend if it exists
frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
