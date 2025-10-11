from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class createTablesXclientDto(BaseModel):
    idClient: int
    name: str
    description: Optional[str] = None
    createDate: Optional[str] = datetime.now().isoformat()

class updateTablesXclientDto(BaseModel):
    idClient: int = None
    name: Optional[str] = None
    description: Optional[str] = None
    updateDate: Optional[str] = datetime.now().isoformat()
    
class TablesXclientDto(BaseModel):
    id: Optional[int] = None
    idClient: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True