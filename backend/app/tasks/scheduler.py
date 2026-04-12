"""C1 自动规则执行（管理员F 负责）

迭代 1 实现：
- C1.3 预约开始 15 分钟后仍未签到自动取消
- C1.4 取消后释放座位
- C1.5 自动记录违约
- C1.6 事务一致
- C1.7 每日刷新自习室动态签到码
"""
import secrets
from datetime import date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.reservation import Reservation, ReservationStatus
from app.models.room import Room
from app.models.user import User
from app.models.violation import Violation


def auto_cancel_no_show():
    """预约开始后超过宽限期仍未签到 -> 违约 + 释放座位"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=settings.checkin_grace_minutes)
        rows = db.query(Reservation).filter(
            Reservation.status == ReservationStatus.PENDING,
            Reservation.start_at <= cutoff,
        ).all()
        for r in rows:
            r.status = ReservationStatus.VIOLATED
            db.add(Violation(user_id=r.user_id, reservation_id=r.id, reason="NO_CHECKIN"))
            user = db.query(User).filter(User.id == r.user_id).first()
            if user:
                user.violation_count = (user.violation_count or 0) + 1
        if rows:
            db.commit()
    finally:
        db.close()


def refresh_daily_checkin_codes():
    """每日 00:05 为每个自习室刷新动态签到码"""
    db = SessionLocal()
    try:
        today = date.today().isoformat()
        for r in db.query(Room).all():
            if r.checkin_code_date != today:
                r.daily_checkin_code = secrets.token_hex(3).upper()  # 6 位
                r.checkin_code_date = today
        db.commit()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone="Asia/Shanghai")
    sched.add_job(auto_cancel_no_show, "interval", minutes=1, id="auto_cancel", replace_existing=True)
    sched.add_job(refresh_daily_checkin_codes, "cron", hour=0, minute=5, id="daily_code", replace_existing=True)
    sched.start()
    # 启动时立刻保证今日码存在
    refresh_daily_checkin_codes()
    return sched
