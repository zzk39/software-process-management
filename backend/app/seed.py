"""初始化数据库 + 灌入 demo 数据：
python -m app.seed
"""
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.room import Room
from app.models.seat import Seat
from app.models.user import User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("已存在数据，跳过 seed")
            return

        db.add_all([
            User(student_no="20230001", name="张三", department="计算机学院",
                 password_hash=hash_password("123456"), is_admin=False),
            User(student_no="20230002", name="李四", department="物理学院",
                 password_hash=hash_password("123456"), is_admin=False),
            User(student_no="admin", name="系统管理员", department="",
                 password_hash=hash_password("admin"), is_admin=True),
        ])

        r1 = Room(name="光华楼一楼自习室", building="光华楼", floor="1")
        r2 = Room(name="图书馆 3F 自习室", building="图书馆", floor="3")
        r3 = Room(name="计算机学院自习室", building="计算机楼", floor="2", department="计算机学院")
        db.add_all([r1, r2, r3])
        db.flush()

        for r in (r1, r2, r3):
            for i in range(1, 11):
                db.add(Seat(
                    room_id=r.id,
                    code=f"{r.id:02d}-{i:03d}",
                    has_power=(i % 3 == 0),
                    near_window=(i <= 4),
                ))
        db.commit()
        print("seed 完成：3 用户 / 3 自习室 / 30 座位")
        print("账号：20230001/123456、20230002/123456、admin/admin")
    finally:
        db.close()


if __name__ == "__main__":
    run()
