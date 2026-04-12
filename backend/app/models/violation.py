from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Violation(Base):
    """违约记录（A7/B5）"""
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"), index=True)
    reason: Mapped[str] = mapped_column(String(64), default="NO_CHECKIN")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
