"""RFC-002 浏览自习室：A1.2(院系过滤)/ A2.1 / A2.5"""
from tests.conftest import auth


def test_department_filter_cs_student_sees_cs_room(app_client, student_token):
    r = app_client.get("/api/rooms", headers=auth(student_token))
    names = [x["name"] for x in r.json()["data"]]
    assert "计算机学院自习室" in names
    assert "光华楼一楼自习室" in names


def test_department_filter_physics_student_cannot_see_cs_room(app_client, student2_token):
    r = app_client.get("/api/rooms", headers=auth(student2_token))
    names = [x["name"] for x in r.json()["data"]]
    assert "计算机学院自习室" not in names
    assert "光华楼一楼自习室" in names


def test_get_room_seats(app_client, student_token):
    r = app_client.get("/api/rooms/1/seats", headers=auth(student_token))
    data = r.json()["data"]
    assert len(data) >= 10  # seed 10 条；其它测试可能追加
    assert all("code" in s for s in data)
