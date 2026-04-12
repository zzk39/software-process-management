from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.core.response import fail
from app.api import auth, rooms, reservations, checkin
from app.api.admin import rooms as admin_rooms, seats as admin_seats, reservations as admin_reservations
from app.tasks.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    sched = start_scheduler()
    yield
    sched.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exc_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(code=exc.status_code, message=str(exc.detail)).model_dump(),
    )


@app.get("/api/health")
def health():
    return {"code": 0, "message": "ok", "data": "up"}


# 学生端路由
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(reservations.router)
app.include_router(checkin.router)

# 管理端路由
app.include_router(admin_rooms.router)
app.include_router(admin_seats.router)
app.include_router(admin_reservations.router)
