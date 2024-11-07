from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True


class FileOut(BaseModel):
    id: int
    filename: str
    upload_count: int

    class Config:
        orm_mode = True