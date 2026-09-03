from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from klip.api.deps import get_current_user
from klip.db import get_db
from klip.models import User
from klip.schemas import TokenPair, UserCreate, UserRead
from klip.services import login_user, register_user

route = APIRouter(prefix="/auth", tags=["auth"])


@route.post("/register", response_model=UserRead, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(user, db)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@route.post("/login", response_model=TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        return login_user(form_data, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@route.get("/me", response_model=UserRead)
def read_current_user(current: User = Depends(get_current_user)):
    return current
