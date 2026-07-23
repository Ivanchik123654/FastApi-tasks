from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from HomeAPI.app.DB.database import Base


class Task(Base):
    __tablename__ = 'tasks'
    id:  Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    done: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)