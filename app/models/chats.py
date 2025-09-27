from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Chats(TimestampMixin, Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    idUser: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    response: Mapped[str] = mapped_column(String(2000), nullable=True)
    source_documents: Mapped[str] = mapped_column(String(4000), nullable=True)

    user: Mapped["Users"] = relationship(back_populates="chats")
    details: Mapped[list["ChatDetails"]] = relationship(back_populates="chat")