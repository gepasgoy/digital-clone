from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Просто храним пользователей в словаре
users = {"admin": "admin123", "user": "password"}

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    if user.username in users and users[user.username] == user.password:
        return {"success": True, "message": f"Welcome {user.username}!"}
    return {"success": False, "message": "Invalid username or password"}