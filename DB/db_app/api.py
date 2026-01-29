from fastapi import FastAPI, HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from authx import AuthX, AuthXConfig
from authx.schema import TokenPayload
from pydantic import BaseModel, Field, EmailStr
from db_app.sqlalchemy_utils.database import get_db
from db_app.sqlalchemy_utils.models import UsersTable


class RegisterModel(BaseModel):
    mail: EmailStr
    password: str 
    Name: str

class AuthModel(BaseModel):
    mail: EmailStr
    password: str

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_token"
config.JWT_TOKEN_LOCATION = ["headers","cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False
# config.JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 час
# config.JWT_REFRESH_TOKEN_EXPIRES = 86400  # 24 часа


security = AuthX(config=config)


def admin_required(db:Session = Depends(get_db), user_id: TokenPayload = Depends(security.access_token_required)):
    user = db.query(UsersTable).filter(
        UsersTable.Id == int(user_id.sub)
    ).first()

    if not user or user.Id != 2:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён"
        )

    return user

@app.post("/register")
def register_user(user: RegisterModel, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(UsersTable).filter(UsersTable.email == user.mail).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )
    new_user = UsersTable(
        email=user.mail,
        Name=user.Name,
        password=user.password
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        return e

@app.post("/login")
def login(creds: AuthModel, response: Response, db: Session = Depends(get_db)):
    user = db.query(UsersTable).filter(UsersTable.email == creds.mail).first()
    
    if not user: return "Пользователь не найден"

    token = security.create_access_token(uid=str(user.Id), )
    refresh_token = security.create_refresh_token(uid=str(user.Id))
    security.set_access_cookies(token,response)
    security.set_refresh_cookies(refresh_token,response)

    return {"access_token": token,
            "refresh_token": refresh_token}
    
    

@app.post("/protected", dependencies=[Depends(security.access_token_required)])
def protected():
    return {"data": "SECRET"}

@app.post("/admin_protected", dependencies=[Depends(security.access_token_required)])
def admin_protected(user: UsersTable = Depends(admin_required)):
    
    return {"data": "SECRET FOR ADMINS"}

@app.post("/refresh", dependencies=[Depends(security.refresh_token_required)])
def refresh_tokens(response: Response):

    new_access_token = security.create_access_token(uid="123")
    security.set_access_cookies(new_access_token, response)

    return {"access_token": new_access_token}

@app.post("/logout")
def logout(response: Response):
    security.unset_access_cookies(response)
    security.unset_refresh_cookies(response)
    return {"message": "Выход выполнен успешно"}