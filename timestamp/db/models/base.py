from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Default:
    """
    Default model with common attributes.

    Attributes:
        created_at (TIMESTAMP): Timestamp when the record was created.
        updated_at (TIMESTAMP): Timestamp when the record was last updated.
    """

    created_at: Mapped[TIMESTAMP] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        server_onupdate=func.now(),
    )
