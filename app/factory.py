from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.api import router
from app.services.container import ServiceContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ServiceContainer(settings)
    container.load()
    app.state.container = container
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="WortMeister API",
        description="German vocabulary learning backend",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app
