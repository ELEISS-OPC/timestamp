from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class Role(Base):
    """
    Role model representing a role in the system.

    Attributes
    ----------
    id : int
        Primary key identifier for the role.
    name : str
        Unique name of the role (e.g., ``admin``, ``officer``, ``employee``).
    """

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship()
