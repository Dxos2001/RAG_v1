import os
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class CreateUsersDto(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    idClient: int
    swt: Optional[bool] = True
    createDate: Optional[str] = datetime.now().isoformat()

class UpdateUsersDto(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    idClient: Optional[int] = None
    swt: Optional[bool] = None
    updateDate: Optional[str] = datetime.now().isoformat()

class UsersDto(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    idClient: int
    swt: bool
    createDate: str
    updateDate: Optional[str] = None

    class Config:
        orm_mode = True