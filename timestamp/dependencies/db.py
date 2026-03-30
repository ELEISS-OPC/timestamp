from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from timestamp.db.database import SessionLocal


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB_Session = Annotated[Session, Depends(get_db_session)]
