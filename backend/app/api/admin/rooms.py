"""B2 自习室管理（管理员D 负责）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import ApiResponse, ok
from app.core.security import require_admin
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomOut

router = APIRouter(prefix="/api/admin/rooms", tags=["admin-rooms"], dependencies=[Depends(require_admin)])


@router.get("", response_model=ApiResponse)
def list_all(db: Session = Depends(get_db)):
    return ok([RoomOut.model_validate(r) for r in db.query(Room).all()])


@router.post("", response_model=ApiResponse)
def create(payload: RoomCreate, db: Session = Depends(get_db)):
    r = Room(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return ok(RoomOut.model_validate(r))


@router.put("/{rid}", response_model=ApiResponse)
def update(rid: int, payload: RoomCreate, db: Session = Depends(get_db)):
    r = db.query(Room).filter(Room.id == rid).first()
    if not r:
        raise HTTPException(404, "自习室不存在")
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return ok(RoomOut.model_validate(r))


@router.delete("/{rid}", response_model=ApiResponse)
def deactivate(rid: int, db: Session = Depends(get_db)):
    r = db.query(Room).filter(Room.id == rid).first()
    if not r:
        raise HTTPException(404, "自习室不存在")
    r.is_active = False
    db.commit()
    return ok()


@router.post("/{rid}/reactivate", response_model=ApiResponse)
def reactivate(rid: int, db: Session = Depends(get_db)):
    """B2.7 反向：把停用的自习室重新启用（修复 Bug-2026-04-12-01）"""
    r = db.query(Room).filter(Room.id == rid).first()
    if not r:
        raise HTTPException(404, "自习室不存在")
    r.is_active = True
    db.commit()
    return ok()
