from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from timestamp.schemas import Role

from .attendance import Attendance
from .base import Base, Default


class User(Base, Default):
    """
    User model representing a user/employee in the system.

    Attributes
    ----------
    id : int
        Primary key identifier for the user.
    first_name : str
        First name of the user.
    middle_name : Optional[str]
        Middle name of the user. May be ``None``.
    last_name : str
        Last name of the user.
    email : str
        Unique email address of the user. May be ``None``.
    password : str
        Hashed password of the user.
    role_id : int
        Foreign key identifier for the role associated with the user (e.g., ``admin (3)``, ``officer (2)``, ``employee (1)``).
    avatar_url : Optional[str]
        URL to the user's avatar image. May be ``None``.
    """

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id"), nullable=False, default=Role.EMPLOYEE.value
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    attendance: Mapped[List["Attendance"]] = relationship()
