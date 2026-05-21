from fastapi import APIRouter

from app.engine.tokenizer import count_tokens, estimate_cost, get_context_window
from pydantic import BaseModel

router = APIRouter(tags=["tokenize"])


class TokenizeRequest(BaseModel):
    text: str
    model: str = "gpt-4"


class TokenizeResponse(BaseModel):
    tokens: int
    cost: float
    model: str
    context_window: int
    usage_pct: float


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize(body: TokenizeRequest):
    tokens = count_tokens(body.text, body.model)
    cost = estimate_cost(tokens, body.model)
    ctx = get_context_window(body.model)
    pct = round((tokens / ctx) * 100, 1) if ctx > 0 else 0
    return TokenizeResponse(tokens=tokens, cost=cost, model=body.model, context_window=ctx, usage_pct=pct)
