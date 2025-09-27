from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class Clients(TimestampMixin, Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ruc: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    contact_email: Mapped[str] = mapped_column(String(100), nullable=True)

    users: Mapped[list["Users"]] = relationship(back_populates="client")
    documents: Mapped[list["Documents"]] = relationship(back_populates="client")
    table_x_clients: Mapped[list["TableXClients"]] = relationship(back_populates="client")