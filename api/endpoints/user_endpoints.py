from fastapi import HTTPException, APIRouter, Request

from core_functions.users import *

from core_functions.limiter import limiter

router = APIRouter()

@router.get("/user/create")
@limiter.limit("5/minute")
def create_user(request: Request):
    pass

@router.get("/user/delete")
@limiter.limit("5/minute")
def delete_user(request: Request):
    pass