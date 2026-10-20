import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.models.car import Car  # noqa: F401 — registra o modelo em Base.metadata antes de init_db()
from app.api.routes.cars import router as cars_router
from app.api.routes.ml import router as ml_router
from app.ml import modelo as ml_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(asyncio.to_thread(ml_model.carregar, Path(settings.ML_MODELS_DIR)))
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars_router, prefix="/api/v1")
app.include_router(ml_router, prefix="/api/v1")
