from fastapi import APIRouter

from app.engine.patterns import list_patterns

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.get("")
async def get_patterns():
    return list_patterns()
