"""RFC-001 学生身份：A1.1, A1.2, A1.4"""
from tests.conftest import auth


def test_login_success(app_client):
    r = app_client.post("/api/auth/login", json={"student_no": "20230001", "password": "123456"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["access_token"]
    assert data["user"]["student_no"] == "20230001"
    assert data["user"]["department"] == "计算机学院"


def test_login_wrong_password(app_client):
    r = app_client.post("/api/auth/login", json={"student_no": "20230001", "password": "bad"})
    assert r.status_code == 401


def test_me_requires_token(app_client):
    r = app_client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_profile(app_client, student_token):
    r = app_client.get("/api/auth/me", headers=auth(student_token))
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "张三"
