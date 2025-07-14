from fastapi import HTTPException, APIRouter, Request

from core_functions.limiter import limiter

router = APIRouter()

@router.get("/test")
@limiter.limit("5/minute")
def test_endpoint(request: Request):
    return {"message": "This is a test endpoint. You can access it 5 times per minute."}