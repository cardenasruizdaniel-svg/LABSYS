from fastapi import APIRouter

from app.api.health import router as health_router
from app.routers import usuarios_router

api_router = APIRouter()

api_router.include_router(
    health_router
)

api_router.include_router(
    usuarios_router
)