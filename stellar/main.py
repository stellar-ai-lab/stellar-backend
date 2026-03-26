from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stellar.api import router
from stellar.config import settings
from stellar.logging_config import setup_logging
from stellar.rate_limiter import rate_limit_config


def configure_cors(application: FastAPI) -> None:
    """Configure CORS for the application."""
    allowed_origins = [
        settings.WEB_APP_URL,
        "http://localhost:3000",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    """Create and configure fastAPI application."""
    setup_logging()

    application = FastAPI(
        title="Stellar Backend",
        description="Stellar backend API endpoints",
    )

    configure_cors(application)
    rate_limit_config(application)
    application.include_router(router)

    return application


app = create_app()
