"""B3 座位管理（管理员D 负责）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import require_admin
from app.models.seat import Seat
from app.schemas.room import SeatCreate, SeatOut

router = APIRouter(prefix="/api/admin/seats", tags=["admin-seats"], dependencies=[Depends(require_admin)])


@router.get("", response_model=ApiResponse)
def list_all(room_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Seat)
    if room_id:
        q = q.filter(Seat.room_id == room_id)
    return ok([SeatOut.model_validate(s) for s in q.all()])


@router.post("", response_model=ApiResponse)
def create(payload: SeatCreate, db: Session = Depends(get_db)):
    s = Seat(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return ok(SeatOut.model_validate(s))


@router.delete("/{sid}", response_model=ApiResponse)
def deactivate(sid: int, db: Session = Depends(get_db)):
    s = db.query(Seat).filter(Seat.id == sid).first()
    if not s:
        raise HTTPException(404, "座位不存在")
    s.is_active = False
    db.commit()
    return ok()
