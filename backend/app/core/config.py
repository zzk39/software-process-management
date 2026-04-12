from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Study Seat Reservation"
    database_url: str = "sqlite:///./study_seat.db"

    jwt_secret: str = "CHANGE-ME-IN-PROD"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # 业务参数（后续可通过 B6 参数管理接口动态覆盖）
    max_reservation_hours: int = 4
    remind_before_minutes: int = 15
    checkin_grace_minutes: int = 15
    late_remind_minutes: int = 10

    cors_origins: list[str] = [
        "http://localhost:5173",  # admin-web
        "http://localhost:5174",  # student-web
    ]


settings = Settings()
