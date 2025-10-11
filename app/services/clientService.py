from typing import List, Optional
from sqlalchemy import select as Select
from sqlalchemy.exc import SQLAlchemyError
from app.models.clients import Clients
from app.schemas.clientsDto import CreateClientsDto, UpdateClientsDto
from sqlalchemy.ext.asyncio import AsyncSession
class clientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_client(self, client_id: int):
        result = await self.db.execute(Select(Clients).where(Clients.id == client_id))
        return result.scalar_one_or_none()
    
    async def get_client_by_ruc(self, ruc: str) -> Optional[Clients]:
        result = await self.db.execute(Select(Clients).where(Clients.ruc == ruc))
        return result.scalar_one_or_none()

    async def get_clients(self, skip: int = 0, limit: int = 100) -> List[Clients]:
        stmt = Select(Clients).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def create_client(self, client_data: CreateClientsDto) -> Optional[Clients]:
        client = Clients(**client_data)
        self.db.add(client)
        try:
            await self.db.commit()
            await self.db.refresh(client)
            return client
        except SQLAlchemyError as e:
            await self.db.rollback()
            print(f"Error creating client: {e}")
            return None
        
    async def update_client(self, client_id: int, client_data: UpdateClientsDto) -> Optional[Clients]:
        client = await self.get_client(client_id)
        if not client:
            return None
        for field, value in client_data.dict(exclude_unset=True).items():
            setattr(client, field, value)
        try:
            await self.db.commit()
            await self.db.refresh(client)
            return client
        except SQLAlchemyError:
            await self.db.rollback()
            return None
    
    async def delete_client(self, client_id: int) -> bool:
        client = await self.get_client(client_id)
        if not client:
            return False
        try:
            await self.db.delete(client)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            return False