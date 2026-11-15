from fastapi import APIRouter
from ..models import GreetingResponse

router = APIRouter(tags=["greeting"])

GREETING = "Hello world!"


@router.get("/api/greeting", response_model=GreetingResponse)
@router.get("/greeting", response_model=GreetingResponse, include_in_schema=False)
async def get_greeting():
    return {"greeting": GREETING}
