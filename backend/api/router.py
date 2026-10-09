from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.users import router as users_router
from backend.api.menu import router as menu_router
from backend.api.recommendations import router as recommendations_router
from backend.api.feedback import router as feedback_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(users_router)
api_router.include_router(menu_router)
api_router.include_router(recommendations_router)
api_router.include_router(feedback_router)

