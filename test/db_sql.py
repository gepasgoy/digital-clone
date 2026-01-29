import sqlite3

with sqlite3.connect("db.db") as db:
    cursor = db.cursor()
    cursor.execute("""SELECT * from users""")
    users = cursor.fetchall()
    print(users)
    cursor.execute("""SELECT * FROM users WHERE Id = 2""")
    users = cursor.fetchall()
    print(users)
    username = 'A1234567'
    password = 1
    user = cursor.execute(""f"select * from users where login = 'A1234567' and password = {password}""").fetchall()
    print(user)