from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
import re, random

app = FastAPI()

# "База"
users = {"user@exam.c": {
        "password": "123123y43gqq34ryqy3r4JHKFSA*%^&@3",
        "height": 180,  
        "weight": 75    
    }}
pending = {}   # временные регистрации


# ----------- МОДЕЛИ -----------

class Step1(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def strong_pass(cls, v):
        if len(v) < 12 or not re.search(r"\d", v) or not re.search(r"[^\w\s]", v):
            raise ValueError("Password >=12, digit + special char required")
        return v


class Step2(BaseModel):
    email: EmailStr
    code: str


class Step3(BaseModel):
    email: EmailStr
    height: int
    weight: int

    @field_validator("height")
    @classmethod
    def h_ok(cls, v):
        if not 100 <= v <= 250:
            raise ValueError("Height 100-250 cm")
        return v

    @field_validator("weight")
    @classmethod
    def w_ok(cls, v):
        if not 30 <= v <= 300:
            raise ValueError("Weight 30-300 kg")
        return v


# ----------- ЭТАП 1 -----------

@app.post("/register/step1")
def reg_step1(data: Step1):
    if data.email in users or data.email in pending:
        raise HTTPException(400, "Email already exists")

    code = str(random.randint(100000, 999999))
    pending[data.email] = {
        "password": data.password,
        "code": code,
        "verified": False
    }

    print(f"[EMAIL EMULATION] Code for {data.email}: {code}")

    return {"ok": True, "msg": "Verification code sent (emulated)"}


# ----------- ЭТАП 2 -----------

@app.post("/register/step2")
def reg_step2(data: Step2):
    p = pending.get(data.email)
    if not p or p["code"] != data.code:
        raise HTTPException(400, "Invalid code")

    p["verified"] = True
    return {"ok": True, "msg": "Email verified"}


# ----------- ЭТАП 3 -----------

@app.post("/register/step3")
def reg_step3(data: Step3):
    p = pending.get(data.email)
    if not p or not p["verified"]:
        raise HTTPException(400, "Email not verified")

    users[data.email] = {
        "password": p["password"],
        "height": data.height,
        "weight": data.weight
    }
    pending.pop(data.email)

    return {"ok": True, "msg": "Registration complete"}


# ----------- ЛОГИН -----------

class Login(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login(data: Login):
    u = users.get(data.email)
    if u and u["password"] == data.password:
        return {"success": True, "message": "Login OK"}
    return {"success": False, "message": "Invalid creds"}
