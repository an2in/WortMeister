"""
WortMeister API entrypoint.

The application is assembled in app/factory.py and split into:
  - routers/controllers
  - services
  - schemas/domain models
"""

from __future__ import annotations

from app.factory import create_app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
