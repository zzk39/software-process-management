from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReservationStatus(StrEnum):
    PENDING = "PENDING"       # 预约中，未签到
    CHECKED_IN = "CHECKED_IN" # 已签到
    CANCELLED = "CANCELLED"   # 用户取消
    VIOLATED = "VIOLATED"     # 违约（超时未签到）
    FINISHED = "FINISHED"     # 已完成（签到后到期）


class Reservation(Base):
    """预约记录（A4/A5/A6/B4）"""
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    status: Mapped[str] = mapped_column(String(16), default=ReservationStatus.PENDING)
    checkin_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
