from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Boolean, func


class Base(DeclarativeBase):
    pass

class TimestampMixin:
    swt: Mapped[bool] = mapped_column(Boolean, default=True)
    createDate: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updateDate: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now())