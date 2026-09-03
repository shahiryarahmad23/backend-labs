from fastapi import APIRouter, Depends,status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from klip.api.deps import get_current_user,require_admin
from klip.db import get_db
from klip.models import User
from klip.schemas import TokenPair, UserCreate, UserRead,RefreshToken
from klip.services import login_user, register_user,refresh_access_token,logout_user
from klip.exceptions import InvalideRefreshToken,RevokedRefreshToken,ExpiredRefreshToken

route = APIRouter(prefix="/auth", tags=["auth"])

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credential",
    headers={"WWW-Authenticate": "Bearer"},
)


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

@route.post("/refresh",response_model = TokenPair)
def refresh(payload: RefreshToken, db: Session = Depends(get_db)):
    try:
        return refresh_access_token(payload,db)
    except (InvalideRefreshToken,RevokedRefreshToken,ExpiredRefreshToken) as e:
        raise credential_exception from e
    
@route.post("/logout",status_code=204)
def logout(payload: RefreshToken, db: Session = Depends(get_db)):
        return logout_user(payload,db)
    
@route.get("/admin",response_model=UserRead)
def admin_access( current_user: User = Depends(require_admin)):
    return current_user
   