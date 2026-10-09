import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(router)

@app.get("/")
def root():
    return {
        "app": "LoopBack API",
        "status": "running",
        "docs": "/docs"
    }
