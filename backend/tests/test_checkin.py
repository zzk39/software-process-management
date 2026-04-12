"""RFC-006 签到：A6.2, A6.4, A6.5"""
from datetime import datetime, timedelta

from tests.conftest import auth


def _make_pending_reservation(app_client, token, seat_id, minutes_from_now=0):
    """直接通过 DB 写入一个 PENDING 预约，绕过 RFC-004 的整点校验用于精确时间控制。"""
    from app.core.database import SessionLocal
    from app.models.reservation import Reservation, ReservationStatus
    from app.models.seat import Seat
    db = SessionLocal()
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()
        now = datetime.utcnow() + timedelta(minutes=minutes_from_now)
        # 取当前用户
        user_id = 1 if token.endswith("=") else 1  # 简化：测试用第一个用户
        from app.core.security import decode_token
        user_id = int(decode_token(token)["sub"])
        r = Reservation(
            user_id=user_id, seat_id=seat.id, room_id=seat.room_id,
            start_at=now, end_at=now + timedelta(hours=1),
            status=ReservationStatus.PENDING,
        )
        db.add(r); db.commit(); db.refresh(r)
        return r.id
    finally:
        db.close()


def test_checkin_wrong_code(app_client, student_token):
    rid = _make_pending_reservation(app_client, student_token, seat_id=6, minutes_from_now=0)
    r = app_client.post("/api/checkin", json={"reservation_id": rid, "code": "WRONGCODE"}, headers=auth(student_token))
    assert r.status_code == 400
    assert "编码" in r.json()["message"]


def test_checkin_outside_window(app_client, student_token):
    # 预约开始于 60 分钟后，远超签到窗口
    rid = _make_pending_reservation(app_client, student_token, seat_id=7, minutes_from_now=60)
    r = app_client.post("/api/checkin", json={"reservation_id": rid, "code": "ANY"}, headers=auth(student_token))
    assert r.status_code == 400
    assert "窗口" in r.json()["message"]


def test_checkin_success(app_client, student_token):
    # 正确的动态码来自 Room.daily_checkin_code
    from app.core.database import SessionLocal
    from app.models.room import Room
    db = SessionLocal()
    code = db.query(Room).filter(Room.id == 1).first().daily_checkin_code
    db.close()
    rid = _make_pending_reservation(app_client, student_token, seat_id=8, minutes_from_now=0)
    r = app_client.post("/api/checkin", json={"reservation_id": rid, "code": code}, headers=auth(student_token))
    assert r.status_code == 200, r.text
    assert "checkin_at" in r.json()["data"]
