from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from timestamp.schemas import Role

from .attendance import Attendance
from .base import Base, Default


class Employee(Base, Default):
    """
    Employee model representing a user in the system.

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
    email : Optional[str]
        Unique email address of the user. May be ``None``.
    password : str
        Hashed password of the user.
    role_id : int
        Foreign key identifier for the role associated with the user (e.g., ``admin (3)``, ``officer (2)``, ``employee (1)``).
    avatar_url : Optional[str]
        URL to the user's avatar image. May be ``None``.
    """

    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(
        ForeignKey("role.id"), nullable=False, default=Role.EMPLOYEE.value
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    attendance: Mapped[List["Attendance"]] = relationship()
