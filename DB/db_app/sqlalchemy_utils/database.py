from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
db_url = "sqlite:///db_app/database.db"

engine = create_engine(db_url, echo=True)

ses = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = ses()
    try:
        yield db
    finally:
        db.close()