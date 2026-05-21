from fastapi import APIRouter

from app.engine.providers.registry import list_providers

router = APIRouter(tags=["providers"])


@router.get("/providers")
async def get_providers():
    return list_providers()
