from database import engine, Base
# from sqlaclhemy.models import 

def create_tables():
    Base.metadata.create_all(engine)