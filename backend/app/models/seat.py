from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Seat(Base):
    """座位（B3）"""
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    code: Mapped[str] = mapped_column(String(32), index=True)  # 座位编号
    has_power: Mapped[bool] = mapped_column(Boolean, default=False)
    near_window: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
