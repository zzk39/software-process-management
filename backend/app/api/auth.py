"""A1 身份识别（学生A 负责）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import create_access_token, get_current_user, verify_password
from app.models.user import User
from app.schemas.auth import LoginIn, LoginOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_no == payload.student_no).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="学号或密码错误")
    token = create_access_token(subject=str(user.id), extra={"is_admin": user.is_admin})
    return ok(LoginOut(access_token=token, user=UserOut.model_validate(user)))


@router.get("/me", response_model=ApiResponse)
def me(current: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(current))
