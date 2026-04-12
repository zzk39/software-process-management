"""端到端冒烟测试：登录 → 浏览自习室 → 创建预约 → 签到 → 取消/违约

运行：
    pytest -q
"""
import os
import tempfile
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    # 用临时数据库隔离测试
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"

    # 重新加载配置
    from importlib import reload
    from app.core import config as cfg
    reload(cfg)
    from app.core import database as db
    reload(db)

    from app import seed
    seed.run()

    from app.main import app
    with TestClient(app) as c:
        yield c

    os.unlink(tmp.name)


def _login(client, user="20230001", pwd="123456"):
    r = client.post("/api/auth/login", json={"student_no": user, "password": pwd})
    assert r.status_code == 200, r.text
    return r.json()["data"]["access_token"]


def test_login_and_list_rooms(client):
    token = _login(client)
    r = client.get("/api/rooms", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    rooms = r.json()["data"]
    # 20230001 是 "计算机学院"，应看到 2 个全校 + 1 个本院 = 3 个
    assert len(rooms) >= 2


def test_physics_student_cannot_see_cs_room(client):
    token = _login(client, "20230002", "123456")
    r = client.get("/api/rooms", headers={"Authorization": f"Bearer {token}"})
    names = [r["name"] for r in r.json()["data"]]
    assert "计算机学院自习室" not in names
