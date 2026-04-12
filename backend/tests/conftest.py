"""共享 fixture：用隔离的临时 SQLite 启动 TestClient。"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app_client():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"

    from importlib import reload
    from app.core import config as cfg; reload(cfg)
    from app.core import database as db; reload(db)

    from app import seed
    seed.run()

    from app.main import app
    with TestClient(app) as c:
        yield c

    os.unlink(tmp.name)


@pytest.fixture
def student_token(app_client):
    r = app_client.post("/api/auth/login", json={"student_no": "20230001", "password": "123456"})
    return r.json()["data"]["access_token"]


@pytest.fixture
def student2_token(app_client):
    r = app_client.post("/api/auth/login", json={"student_no": "20230002", "password": "123456"})
    return r.json()["data"]["access_token"]


@pytest.fixture
def admin_token(app_client):
    r = app_client.post("/api/auth/login", json={"student_no": "admin", "password": "admin"})
    return r.json()["data"]["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}
