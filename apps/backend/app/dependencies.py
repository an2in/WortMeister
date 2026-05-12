from __future__ import annotations

from typing import cast

from fastapi import Header, HTTPException, Request

from app.services.container import ServiceContainer


def get_container(request: Request) -> ServiceContainer:
    return cast(ServiceContainer, request.app.state.container)


def get_user_id(x_user_id: str = Header(default="")) -> str:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header is required")
    return x_user_id
