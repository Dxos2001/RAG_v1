from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class ChatDetails(TimestampMixin, Base):
    __tablename__ = "chat_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    idChat: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    detail: Mapped[str] = mapped_column(String(2000), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'user', 'system', 'bot'
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    chat: Mapped["Chats"] = relationship(back_populates="details")