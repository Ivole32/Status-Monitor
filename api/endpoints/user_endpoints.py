from fastapi import HTTPException, APIRouter, Request

from core_functions.users import users

from core_functions.limiter import limiter

router = APIRouter()
user_manager = users()

@router.get("/user/create")
@limiter.limit("5/minute")
def create_user(request: Request, username: str, email: str, password: str):
    user_manager.create_user(username, email, password)

@router.get("/user/delete")
@limiter.limit("5/minute")
def delete_user(request: Request):
    pass