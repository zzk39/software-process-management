"""A2 浏览自习室与座位（学生A 负责）"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import get_current_user
from app.models.room import Room
from app.models.seat import Seat
from app.models.user import User
from app.schemas.room import RoomOut, SeatOut

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=ApiResponse)
def list_rooms(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    q = db.query(Room).filter(Room.is_active == True)
    # 院系限制：院系专属自习室仅向本院系学生开放
    rows = [
        r for r in q.all()
        if not r.department or r.department == current.department
    ]
    return ok([RoomOut.model_validate(r) for r in rows])


@router.get("/{room_id}", response_model=ApiResponse)
def get_room(room_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == room_id, Room.is_active == True).first()
    if not room:
        return ok(None, message="room not found")
    return ok(RoomOut.model_validate(room))


@router.get("/{room_id}/seats", response_model=ApiResponse)
def list_seats(room_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    seats = db.query(Seat).filter(Seat.room_id == room_id, Seat.is_active == True).all()
    return ok([SeatOut.model_validate(s) for s in seats])
