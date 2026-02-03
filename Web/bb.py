# simple_api.py (FastAPI)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
users = {"admin": "admin123"}

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    if user.username in users and users[user.username] == user.password:
        return {"success": True, "message": f"Welcome {user.username}"}
    return {"success": False, "message": "Invalid credentials"}

# simple_app.py (Streamlit)
import streamlit as st
import requests

st.title("Simple Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    response = requests.post("http://localhost:8000/login", 
                           json={"username": username, "password": password})
    if response.json()["success"]:
        st.success("Login successful!")
    else:
        st.error("Login failed!")