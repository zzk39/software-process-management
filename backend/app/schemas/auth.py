from pydantic import BaseModel


class LoginIn(BaseModel):
    student_no: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    student_no: str
    name: str
    department: str
    is_admin: bool
    violation_count: int

    class Config:
        from_attributes = True


LoginOut.model_rebuild()
