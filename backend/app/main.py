from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.debug.middleware import DebugMiddleware
from app.routers import routers

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Transform raw ideas into well-structured AI prompts.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DebugMiddleware)

for router in routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "ok"}
