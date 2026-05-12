from __future__ import annotations

from typing import cast

from fastapi import Request

from app.services.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    return cast(ServiceContainer, request.app.state.container)
