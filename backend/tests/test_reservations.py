"""RFC-004 创建预约：A4.1, A4.2, A4.3, A4.5, A4.7, A4.10
RFC-005 取消：A5.2, A5.4"""
from datetime import datetime, timedelta

from tests.conftest import auth


def _future_slot(day_offset=1, hour=10):
    """用明天/后天的某个白天整点，保证落在自习室 07:00-22:00 内且互不冲突。"""
    base = (datetime.utcnow() + timedelta(days=day_offset)).replace(hour=hour, minute=0, second=0, microsecond=0)
    return base.isoformat()


def _next_hour(hours_ahead=1):
    """向上取下一个整点，仅用于'整点校验'类测试。"""
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    return (now + timedelta(hours=hours_ahead)).isoformat()


def test_create_must_be_whole_hour(app_client, student_token):
    bad = datetime.utcnow().replace(minute=30).isoformat()
    r = app_client.post("/api/reservations", json={"seat_id": 1, "start_at": bad, "hours": 2}, headers=auth(student_token))
    assert r.status_code == 400


def test_create_hours_limit(app_client, student_token):
    r = app_client.post("/api/reservations",
                        json={"seat_id": 1, "start_at": _next_hour(), "hours": 5},
                        headers=auth(student_token))
    assert r.status_code == 400


def test_create_department_forbidden(app_client, student2_token):
    # 物理学院学生预约计算机学院教室的座位（seed 中 room 3 的座位 id 21-30）
    r = app_client.post("/api/reservations",
                        json={"seat_id": 21, "start_at": _next_hour(), "hours": 1},
                        headers=auth(student2_token))
    assert r.status_code == 403


def test_create_and_cancel_flow(app_client, student_token):
    start = _future_slot(day_offset=1, hour=10)
    r = app_client.post("/api/reservations",
                        json={"seat_id": 2, "start_at": start, "hours": 2},
                        headers=auth(student_token))
    assert r.status_code == 200, r.text
    rid = r.json()["data"]["id"]

    # 取消
    r2 = app_client.post(f"/api/reservations/{rid}/cancel", headers=auth(student_token))
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "CANCELLED"


def test_seat_conflict(app_client, student_token):
    start = _future_slot(day_offset=2, hour=14)
    ok = app_client.post("/api/reservations",
                         json={"seat_id": 3, "start_at": start, "hours": 2},
                         headers=auth(student_token))
    assert ok.status_code == 200
    # 同座位同时段，另一用户冲突
    r = app_client.post("/api/reservations",
                        json={"seat_id": 3, "start_at": start, "hours": 1},
                        headers=auth(student_token))
    assert r.status_code == 409


def test_user_double_booking(app_client, student_token):
    start = _future_slot(day_offset=3, hour=15)
    r1 = app_client.post("/api/reservations",
                         json={"seat_id": 4, "start_at": start, "hours": 2},
                         headers=auth(student_token))
    assert r1.status_code == 200
    # 同一用户相同时段预约另一座位
    r2 = app_client.post("/api/reservations",
                         json={"seat_id": 5, "start_at": start, "hours": 1},
                         headers=auth(student_token))
    assert r2.status_code == 409
