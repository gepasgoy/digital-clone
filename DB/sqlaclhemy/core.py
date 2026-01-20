from database import engine, Base, ses

def create_tables():
    Base.metadata.create_all(engine)

def drop_tables():
    Base.metadata.drop_all(engine)
    
data = [{"Name":"Boba"}]

def insert_data(cl):
    session = ses()
    session.bulk_insert_mappings(cl, data)
    session.commit()