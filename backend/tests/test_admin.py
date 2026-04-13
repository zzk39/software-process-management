"""RFC-011/012/013 管理端 CRUD 与查询"""
from tests.conftest import auth


def test_admin_requires_admin_role(app_client, student_token):
    r = app_client.get("/api/admin/rooms", headers=auth(student_token))
    assert r.status_code == 403


def test_admin_room_crud(app_client, admin_token):
    # 创建
    r = app_client.post("/api/admin/rooms", headers=auth(admin_token),
                        json={"name": "测试自习室", "building": "X", "floor": "1"})
    assert r.status_code == 200
    rid = r.json()["data"]["id"]

    # 列表可见
    rooms = app_client.get("/api/admin/rooms", headers=auth(admin_token)).json()["data"]
    assert any(x["id"] == rid for x in rooms)

    # 停用
    r = app_client.delete(f"/api/admin/rooms/{rid}", headers=auth(admin_token))
    assert r.status_code == 200

    # 停用后 is_active=false
    rooms = app_client.get("/api/admin/rooms", headers=auth(admin_token)).json()["data"]
    assert next(x for x in rooms if x["id"] == rid)["is_active"] is False

    # 重新启用（Bug-2026-04-12-01）
    r = app_client.post(f"/api/admin/rooms/{rid}/reactivate", headers=auth(admin_token))
    assert r.status_code == 200
    rooms = app_client.get("/api/admin/rooms", headers=auth(admin_token)).json()["data"]
    assert next(x for x in rooms if x["id"] == rid)["is_active"] is True


def test_admin_seat_create_and_list(app_client, admin_token):
    r = app_client.post("/api/admin/seats", headers=auth(admin_token),
                        json={"room_id": 1, "code": "TEST-01", "has_power": True, "near_window": False})
    assert r.status_code == 200
    sid = r.json()["data"]["id"]

    seats = app_client.get("/api/admin/seats?room_id=1", headers=auth(admin_token)).json()["data"]
    assert any(s["id"] == sid for s in seats)


def test_admin_seat_duplicate_code_rejected(app_client, admin_token):
    """Bug-2026-04-13-05 / RFC-012 §6：同一自习室不允许重复 code。"""
    payload = {"room_id": 1, "code": "DUP-CODE-01", "has_power": False, "near_window": False}
    r1 = app_client.post("/api/admin/seats", headers=auth(admin_token), json=payload)
    assert r1.status_code == 200
    r2 = app_client.post("/api/admin/seats", headers=auth(admin_token), json=payload)
    assert r2.status_code == 409
    # 不同自习室可以复用同一个 code
    r3 = app_client.post("/api/admin/seats", headers=auth(admin_token),
                         json={**payload, "room_id": 2})
    assert r3.status_code == 200


def test_admin_seat_update(app_client, admin_token):
    """RFC-012 B3.3-B3.4：编辑座位属性（编号、插座、靠窗）。"""
    r = app_client.post("/api/admin/seats", headers=auth(admin_token),
                        json={"room_id": 1, "code": "EDIT-SRC", "has_power": False, "near_window": False})
    assert r.status_code == 200
    sid = r.json()["data"]["id"]

    # 正常编辑
    r = app_client.put(f"/api/admin/seats/{sid}", headers=auth(admin_token),
                       json={"room_id": 1, "code": "EDIT-DST", "has_power": True, "near_window": True})
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    assert body["code"] == "EDIT-DST" and body["has_power"] and body["near_window"]

    # 改成与同 room 内另一行重复的 code → 409
    r2 = app_client.post("/api/admin/seats", headers=auth(admin_token),
                         json={"room_id": 1, "code": "EDIT-OTHER"})
    assert r2.status_code == 200
    r3 = app_client.put(f"/api/admin/seats/{sid}", headers=auth(admin_token),
                        json={"room_id": 1, "code": "EDIT-OTHER"})
    assert r3.status_code == 409

    # 不存在的 id → 404
    r4 = app_client.put("/api/admin/seats/999999", headers=auth(admin_token),
                        json={"room_id": 1, "code": "X"})
    assert r4.status_code == 404


def test_admin_seat_deactivate_and_reactivate(app_client, admin_token):
    """Bug-2026-04-13-02：停用的座位必须可以重新启用"""
    r = app_client.post("/api/admin/seats", headers=auth(admin_token),
                        json={"room_id": 1, "code": "TEST-REACT-01", "has_power": False, "near_window": False})
    assert r.status_code == 200
    sid = r.json()["data"]["id"]

    # 停用
    r = app_client.delete(f"/api/admin/seats/{sid}", headers=auth(admin_token))
    assert r.status_code == 200
    seats = app_client.get("/api/admin/seats?room_id=1", headers=auth(admin_token)).json()["data"]
    assert next(s for s in seats if s["id"] == sid)["is_active"] is False

    # 重新启用
    r = app_client.post(f"/api/admin/seats/{sid}/reactivate", headers=auth(admin_token))
    assert r.status_code == 200
    seats = app_client.get("/api/admin/seats?room_id=1", headers=auth(admin_token)).json()["data"]
    assert next(s for s in seats if s["id"] == sid)["is_active"] is True


def test_admin_reservations_query(app_client, admin_token):
    r = app_client.get("/api/admin/reservations", headers=auth(admin_token))
    assert r.status_code == 200
    # seed 后可能无预约；只校验接口可用
    assert isinstance(r.json()["data"], list)
