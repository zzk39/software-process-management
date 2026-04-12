from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Room(Base):
    """自习室（B2）"""
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    building: Mapped[str] = mapped_column(String(64), default="")
    floor: Mapped[str] = mapped_column(String(16), default="")
    department: Mapped[str] = mapped_column(String(64), default="")  # 空=全校开放
    # 开放时间，格式 "HH:MM"
    open_time: Mapped[str] = mapped_column(String(5), default="07:00")
    close_time: Mapped[str] = mapped_column(String(5), default="22:00")
    is_overnight: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 每日动态签到码，由调度任务刷新
    daily_checkin_code: Mapped[str] = mapped_column(String(16), default="")
    checkin_code_date: Mapped[str] = mapped_column(String(10), default="")  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
