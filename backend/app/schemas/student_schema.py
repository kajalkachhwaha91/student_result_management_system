from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    course: str
    classname : str 

class StudentCreate(StudentBase):
    pass

class StudentDB(StudentBase):
    id: str

    class Config:
        orm_mode = True
