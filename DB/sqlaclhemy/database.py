from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
db_url = "sqlite:///database.db"

engine = create_engine(db_url, echo=True)

ses = sessionmaker(engine)

class Base(DeclarativeBase):
    pass