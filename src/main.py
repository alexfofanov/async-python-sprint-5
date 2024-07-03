from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from src.api.v1.base import api_router
from src.core.config import app_settings
from src.services.minio import minio_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await minio_handler.create_backet(app_settings.minio_bucket_name)
    yield


app = FastAPI(
    title=app_settings.app_title,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api/v1')
exclude_prefixes = ['/api/v1/users/', '/api/openapi', '/api/v1/ping']


@app.exception_handler(RequestValidationError)
async def handle_error(
    request: Request, exc: RequestValidationError
) -> PlainTextResponse:
    return PlainTextResponse(str(exc.errors()), status_code=400)


if __name__ == '__main__':
    host = app_settings.project_host
    uvicorn.run(
        'main:app',
        host=str(app_settings.project_host),
        port=app_settings.project_port,
        reload=True,
    )
