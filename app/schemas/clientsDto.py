from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CreateClientsDto(BaseModel):
    ruc: str
    name: str
    api_key: Optional[str] = None
    contact_email: Optional[str] = None
    swt: Optional[bool] = True
    createDate: Optional[str] = datetime.now().isoformat()

class UpdateClientsDto(BaseModel):
    ruc: Optional[str] = None
    name: Optional[str] = None
    api_key: Optional[str] = None
    contact_email: Optional[str] = None
    swt: Optional[bool] = None
    updateDate: Optional[str] = datetime.now().isoformat()

class ClientsDto(BaseModel):
    id: Optional[int] = None
    ruc: str
    name: str
    api_key: Optional[str] = None
    contact_email: Optional[str] = None
    swt: bool

    class Config:
        orm_mode = True
