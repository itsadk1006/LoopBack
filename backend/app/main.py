import logging
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loopback.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing LoopBack backend application...")
    active_mode = database.init_database()
    logger.info(f"Database initialized in mode: {active_mode}")
    yield
    logger.info("Shutting down LoopBack backend application.")

app = FastAPI(
    title="LoopBack API",
    description="Agentic Recycling Failure Investigation System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "evidence")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=UPLOAD_DIR), name="evidence")

app.include_router(router)

@app.get("/")
def root():
    return {
        "app": "LoopBack API",
        "status": "running",
        "docs": "/docs"
    }
