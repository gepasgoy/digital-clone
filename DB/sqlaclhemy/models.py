from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class WorkersBase(Base):
    __tablename__ = "Workers"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)