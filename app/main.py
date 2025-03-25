from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import engine, Base

# Import routers from endpoints and views
from app.routers.pull_shopify import router as pull_shopify_router
from app.routers.pull_google_ads import router as pull_google_ads_router
from app.routers.dashboard_data import router as dashboard_data_router
from app.views.dashboard import router as dashboard_view_router

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Include routers
    app.include_router(pull_shopify_router)
    app.include_router(pull_google_ads_router)
    app.include_router(dashboard_data_router)
    app.include_router(dashboard_view_router)

    return app

app = create_app()
