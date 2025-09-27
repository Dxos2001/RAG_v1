from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.users import Users
from app.schemas.usersDto import CreateUsersDto, UpdateUsersDto
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_user(self, user_id: int) -> Optional[Users]:
        result = await self.db.execute(select(Users).where(Users.id == user_id))
        return result.scalar_one_or_none()

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[Users]:
        stmt = select(Users).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, user_in: CreateUsersDto) -> Optional[Users]:
        user = Users(**user_in.dict())
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.db.rollback()
            print(f"Error creating user: {e}")
            return None

    async def update_user(self, user_id: int, user_in: UpdateUsersDto) -> Optional[Users]:
        user = await self.get_user(user_id)
        if not user:
            return None
        for field, value in user_in.dict(exclude_unset=True).items():
            setattr(user, field, value)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError:
            await self.db.rollback()
            return None

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        try:
            await self.db.delete(user)
            await self.db.commit()
            return True
        except SQLAlchemyError:
            await self.db.rollback()
            return False