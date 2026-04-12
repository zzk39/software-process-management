"""A4 + A5 创建/取消预约（林佳航 负责）

迭代 1 需实现的 Story：
- A4.1 按整点+时长创建预约
- A4.2 仅允许整点
- A4.3 最多 4 小时（取 settings.max_reservation_hours）
- A4.5 时段冲突校验
- A4.6 必须在自习室开放时间内
- A4.10 同一时间段不能有多个有效预约
- A5.2 取消尚未开始的预约
- A5.4 取消后座位立即可用
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import get_current_user
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import Room
from app.models.seat import Seat
from app.models.user import User

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


class ReservationCreate(BaseModel):
    seat_id: int
    start_at: datetime  # ISO 格式
    hours: int  # 1~max


class ReservationOut(BaseModel):
    id: int
    seat_id: int
    room_id: int
    start_at: datetime
    end_at: datetime
    status: str

    class Config:
        from_attributes = True


def _validate_start_hour(dt: datetime):
    if dt.minute != 0 or dt.second != 0:
        raise HTTPException(400, "预约必须为整点")


def _within_room_hours(room: Room, start: datetime, end: datetime):
    if room.is_overnight:
        return
    oh, om = map(int, room.open_time.split(":"))
    ch, cm = map(int, room.close_time.split(":"))
    day = start.date()
    open_dt = datetime.combine(day, datetime.min.time()).replace(hour=oh, minute=om)
    close_dt = datetime.combine(day, datetime.min.time()).replace(hour=ch, minute=cm)
    if start < open_dt or end > close_dt:
        raise HTTPException(400, f"须在自习室开放时间 {room.open_time}-{room.close_time} 内")


@router.post("", response_model=ApiResponse)
def create_reservation(
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    _validate_start_hour(payload.start_at)
    if not (1 <= payload.hours <= settings.max_reservation_hours):
        raise HTTPException(400, f"时长需在 1~{settings.max_reservation_hours} 小时之间")

    seat = db.query(Seat).filter(Seat.id == payload.seat_id, Seat.is_active == True).first()
    if not seat:
        raise HTTPException(404, "座位不存在或已停用")
    room = db.query(Room).filter(Room.id == seat.room_id, Room.is_active == True).first()
    if not room:
        raise HTTPException(404, "自习室不可用")
    if room.department and room.department != current.department:
        raise HTTPException(403, "无权预约该院系自习室")

    end_at = payload.start_at + timedelta(hours=payload.hours)
    _within_room_hours(room, payload.start_at, end_at)

    # 同座位时段冲突
    conflict = db.query(Reservation).filter(
        Reservation.seat_id == seat.id,
        Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CHECKED_IN]),
        Reservation.start_at < end_at,
        Reservation.end_at > payload.start_at,
    ).first()
    if conflict:
        raise HTTPException(409, "该座位此时段已被预约")

    # 同一用户时段冲突（A4.10）
    user_conflict = db.query(Reservation).filter(
        Reservation.user_id == current.id,
        Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CHECKED_IN]),
        Reservation.start_at < end_at,
        Reservation.end_at > payload.start_at,
    ).first()
    if user_conflict:
        raise HTTPException(409, "同一时间段你已有其它预约")

    r = Reservation(
        user_id=current.id,
        seat_id=seat.id,
        room_id=room.id,
        start_at=payload.start_at,
        end_at=end_at,
        status=ReservationStatus.PENDING,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return ok(ReservationOut.model_validate(r))


@router.get("/me", response_model=ApiResponse)
def my_reservations(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    rows = (
        db.query(Reservation)
        .filter(Reservation.user_id == current.id)
        .order_by(Reservation.start_at.desc())
        .all()
    )
    return ok([ReservationOut.model_validate(r) for r in rows])


@router.post("/{rid}/cancel", response_model=ApiResponse)
def cancel_reservation(rid: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    r = db.query(Reservation).filter(Reservation.id == rid, Reservation.user_id == current.id).first()
    if not r:
        raise HTTPException(404, "预约不存在")
    if r.status != ReservationStatus.PENDING:
        raise HTTPException(400, f"当前状态 {r.status} 不可取消")
    if r.start_at <= datetime.utcnow():
        raise HTTPException(400, "预约已开始，不可取消")
    r.status = ReservationStatus.CANCELLED
    r.cancelled_at = datetime.utcnow()
    db.commit()
    return ok(ReservationOut.model_validate(r))
