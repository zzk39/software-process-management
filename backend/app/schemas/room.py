from pydantic import BaseModel


class RoomOut(BaseModel):
    id: int
    name: str
    building: str
    floor: str
    department: str
    open_time: str
    close_time: str
    is_overnight: bool
    is_active: bool

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    name: str
    building: str = ""
    floor: str = ""
    department: str = ""
    open_time: str = "07:00"
    close_time: str = "22:00"
    is_overnight: bool = False


class SeatOut(BaseModel):
    id: int
    room_id: int
    code: str
    has_power: bool
    near_window: bool
    is_active: bool

    class Config:
        from_attributes = True


class SeatCreate(BaseModel):
    room_id: int
    code: str
    has_power: bool = False
    near_window: bool = False
