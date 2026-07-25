"""The FastAPI application.

The expensive objects are built once in the lifespan and hung off ``app.state``; nothing
in a request handler constructs a store, a searcher or a provider.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from vault_spider.web.state import AppState, build_state
from vault_spider.web.views import router

STATIC_DIR = Path(__file__).parent / "static"


def create_app(state_factory: Optional[Callable[[], AppState]] = None) -> FastAPI:
    """Build the app. ``state_factory`` is the seam tests use to inject a fake vault."""
    factory = state_factory or build_state

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.vault = factory()
        yield

    app = FastAPI(
        title="Vault Spider",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(router)
    return app
