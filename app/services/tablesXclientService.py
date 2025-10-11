from typing import List, Optional
from sqlalchemy import select as Select
from sqlalchemy.exc import SQLAlchemyError
from app.models.tableXClients import TableXClients
from app.schemas.tablesXclientDto import createTablesXclientDto, updateTablesXclientDto
from sqlalchemy.ext.asyncio import AsyncSession
class tablesXclientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_table_by_id(self, table_id: int) -> Optional[TableXClients]:
        result = await self.db.execute(Select(TableXClients).where(TableXClients.id == table_id))
        return result.scalar_one_or_none()

    async def get_tables(self, skip: int = 0, limit: int = 100) -> List[TableXClients]:
        stmt = Select(TableXClients).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_table(self, table_data: createTablesXclientDto) -> Optional[TableXClients]:
        table = TableXClients(**table_data.dict())
        self.db.add(table)
        try:
            await self.db.commit()
            await self.db.refresh(table)
            return table
        except SQLAlchemyError as e:
            await self.db.rollback()
            print(f"Error creating table: {e}")
            return None

    async def update_table(self, table_id: int, table_data: updateTablesXclientDto) -> Optional[TableXClients]:
        table = await self.get_table_by_id(table_id)
        if not table:
            return None
        for field, value in table_data.dict(exclude_unset=True).items():
            setattr(table, field, value)
        try:
            await self.db.commit()
            await self.db.refresh(table)
            return table
        except SQLAlchemyError:
            await self.db.rollback()
            return None

    async def delete_table(self, table_id: int) -> bool:
        table = await self.get_table_by_id(table_id)
        if not table:
            return False
        try:
            await self.db.delete(table)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            return False