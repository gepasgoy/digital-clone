from os import getenv
from dotenv import load_dotenv 
import psycopg2

load_dotenv("config.env")

port =  getenv('$PORT')

try: 
    connection = psycopg2.connect(
        host = getenv('$HOST'),
        user = getenv('$USER'),
        password = getenv('$PSSWD'),
        database = getenv('$DBNAME')
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version()"
        )
    
    print(cursor.fetchall())

    
except Exception as e: print(f"error: {e}")
finally: 
    if connection: 
        connection.close()
        print("Закрыто")
