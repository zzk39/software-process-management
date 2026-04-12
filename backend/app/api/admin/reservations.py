"""B4 管理端预约管理（zzk 负责）

迭代 1 实现：
- B4.1 查看所有预约
- B4.2 按学生、自习室、日期筛选
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import require_admin
from app.models.reservation import Reservation
from app.models.user import User

router = APIRouter(prefix="/api/admin/reservations", tags=["admin-reservations"], dependencies=[Depends(require_admin)])


@router.get("", response_model=ApiResponse)
def list_all(
    db: Session = Depends(get_db),
    student_no: str | None = Query(None),
    room_id: int | None = Query(None),
    date: str | None = Query(None, description="YYYY-MM-DD"),
    status: str | None = Query(None),
):
    q = db.query(Reservation)
    if student_no:
        uid = db.query(User.id).filter(User.student_no == student_no).scalar()
        q = q.filter(Reservation.user_id == uid) if uid else q.filter(False)
    if room_id:
        q = q.filter(Reservation.room_id == room_id)
    if status:
        q = q.filter(Reservation.status == status)
    if date:
        d = datetime.strptime(date, "%Y-%m-%d")
        q = q.filter(Reservation.start_at >= d, Reservation.start_at < d.replace(hour=23, minute=59, second=59))
    rows = q.order_by(Reservation.start_at.desc()).limit(500).all()
    return ok([
        {
            "id": r.id,
            "user_id": r.user_id,
            "seat_id": r.seat_id,
            "room_id": r.room_id,
            "start_at": r.start_at.isoformat(),
            "end_at": r.end_at.isoformat(),
            "status": r.status,
        } for r in rows
    ])
