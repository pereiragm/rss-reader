from fastapi import APIRouter

from app.api.v1 import endpoints, endpoints_auth

api_router = APIRouter()
api_router.include_router(endpoints.router)
api_router.include_router(endpoints_auth.router)
