"""A6 签到（林佳航 负责）

迭代 1 实现：
- A6.2 Web 端输入动态编码签到
- A6.4 仅在预约时间附近可签到（±15 分钟）
- A6.5 校验编码对应教室与预约教室一致
- A6.6 返回签到时间戳
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
from app.models.user import User

router = APIRouter(prefix="/api/checkin", tags=["checkin"])


class CheckinIn(BaseModel):
    reservation_id: int
    code: str


@router.post("", response_model=ApiResponse)
def checkin(payload: CheckinIn, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    r = db.query(Reservation).filter(
        Reservation.id == payload.reservation_id,
        Reservation.user_id == current.id,
    ).first()
    if not r:
        raise HTTPException(404, "预约不存在")
    if r.status != ReservationStatus.PENDING:
        raise HTTPException(400, f"当前状态 {r.status} 不可签到")

    now = datetime.utcnow()
    grace = timedelta(minutes=settings.checkin_grace_minutes)
    if now < r.start_at - grace or now > r.start_at + grace:
        raise HTTPException(400, "不在签到允许时间窗口内")

    room = db.query(Room).filter(Room.id == r.room_id).first()
    if not room or room.daily_checkin_code != payload.code.strip():
        raise HTTPException(400, "签到编码错误或已失效")

    r.status = ReservationStatus.CHECKED_IN
    r.checkin_at = now
    db.commit()
    db.refresh(r)
    return ok({"reservation_id": r.id, "checkin_at": r.checkin_at.isoformat()})
