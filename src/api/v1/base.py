from fastapi import APIRouter

from src.api.v1.file import file_router
from src.api.v1.ping import ping_router
from src.api.v1.user import user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix='/users', tags=['user'])
api_router.include_router(file_router, prefix='/files', tags=['file'])
api_router.include_router(ping_router, prefix='/ping', tags=['ping'])
