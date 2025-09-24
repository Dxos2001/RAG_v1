from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin

class TableXClients(TimestampMixin, Base):
    __tablename__ = "table_x_clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    idClient: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    client: Mapped["Clients"] = relationship(back_populates="table_x_clients")