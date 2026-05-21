from fastapi import APIRouter

from app.engine.tokenizer import count_tokens, estimate_cost
from pydantic import BaseModel

router = APIRouter(tags=["tokenize"])


class TokenizeRequest(BaseModel):
    text: str
    model: str = "gpt-4"


class TokenizeResponse(BaseModel):
    tokens: int
    cost: float
    model: str


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize(body: TokenizeRequest):
    tokens = count_tokens(body.text, body.model)
    cost = estimate_cost(tokens, body.model)
    return TokenizeResponse(tokens=tokens, cost=cost, model=body.model)
