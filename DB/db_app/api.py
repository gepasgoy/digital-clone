from fastapi import FastAPI, HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from authx import AuthX, AuthXConfig
from authx.schema import TokenPayload
from pydantic import BaseModel, Field, EmailStr, validator
from db_app.sqlalchemy_utils.database import get_db # type: ignore
from db_app.sqlalchemy_utils.models import UsersTable, PatientsTable, ResearchTable, PulseMonitoringTable # type: ignore


class AuthModel(BaseModel):
    mail: EmailStr
    password: str

class RegisterModel(AuthModel):
    Name: str

class PulseMonitoringInput(BaseModel):
    value: int
    patient_id: int|None = None  # Если не указан, используется ID текущего пользователя
    
    #Валидатор на всякий оставил, мб пригодится
    @validator('value')
    def validate_value(cls, v):
        if v <= 0:
            raise ValueError('Значение должно быть положительным')
        if v > 300:
            raise ValueError('Значение слишком велико')
        return v

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_token"
config.JWT_TOKEN_LOCATION = ["headers","cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False


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

def get_patient(db: Session = Depends(get_db), patient_id:int=-1):
    patient = db.query(PatientsTable).filter(
            PatientsTable.Id == patient_id
        ).first()
    return patient
            

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

@app.get("/medical-card", dependencies=[Depends(security.access_token_required)])
def get_medical_card(
    patient_id: int | None = None,
    db: Session = Depends(get_db)
):
    try:
        
        # Находим пациента
        patient: UsersTable = get_patient(db=db,patient_id=patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Пациент не найден"
            )
        
        # # Получаем историю посещений
        # visits = db.query(VisitsTable).filter(
        #     VisitsTable.PatientId == target_patient_id
        # ).order_by(VisitsTable.VisitDate.desc()).all()
        
        # # Получаем назначенные лечения
        # treatments = db.query(AssignedTreatmentTable).filter(
        #     AssignedTreatmentTable.PatientId == target_patient_id
        # ).order_by(AssignedTreatmentTable.TreatmentDate.desc()).all()
        
        # Получаем медицинские исследования
        research = db.query(ResearchTable).filter(
            ResearchTable.PatientId == patient_id
        ).order_by(ResearchTable.EventDate.desc()).all()
        
        # Получаем мониторинг пульса
        pulse_monitoring = db.query(PulseMonitoringTable).filter(
            PulseMonitoringTable.PatientId == patient_id
        ).order_by(PulseMonitoringTable.CreatedAt.desc()).limit(30).all()
        
        # Формируем ответ
        medical_card = {
            "patient_info": {
                "id": patient.Id,
                "full_name": f"{patient.SecondName} {patient.FirstName} {patient.Patronomyc}",
                "age": patient.Age,
                "snils": patient.SNILS,
                "polis": patient.POLIS
            },
            # "visits_history": [
            #     {
            #         "id": visit.Id,
            #         "date": visit.VisitDate,
            #         "complain": visit.Complain,
            #         "symptoms": visit.Symptoms
            #     } for visit in visits
            # ],
            # "treatments": [
            #     {
            #         "id": treatment.Id,
            #         "date": treatment.TreatmentDate,
            #         "treatment_scheme": treatment.TreatmentScheme
            #     } for treatment in treatments
            # ],
            "research": [
                {
                    "id": r.Id,
                    "name": r.Name,
                    "date": r.EventDate,
                    "state": r.State,
                    "result": r.Result
                } for r in research
            ],
            "pulse_monitoring": [
                {
                    "id": pm.Id,
                    "date": pm.CreatedAt,
                    "value": pm.Value
                } for pm in pulse_monitoring
            ]
        }
        
        return medical_card
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении медицинской карты: {str(e)}"
        )
    

# КРИТЕРИЙ 2: Метод для ввода данных самоконтроля
@app.post("/pulse-monitoring", dependencies=[Depends(security.access_token_required)])
def add_pulse_monitoring(
    data: PulseMonitoringInput,
    db: Session = Depends(get_db)
):
    """
    Добавление данных самоконтроля пульса.
    """
    try:
        # Определяем ID пациента
        patient_id = data.patient_id
        
        patient = get_patient(db,patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Пациент не найден"
            )
        
        pulse_record = PulseMonitoringTable(
            PatientId=patient_id,
            Value=data.value
        )
        
        db.add(pulse_record)
        db.commit()
        db.refresh(pulse_record)
        
        return {
            "message": "Данные самоконтроля успешно сохранены",
            "record_id": pulse_record.Id,
            "patient_id": pulse_record.PatientId,
            "patient_name": patient.FirstName,
            "value": pulse_record.Value,
            "created_at": pulse_record.CreatedAt
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при сохранении данных: {str(e)}")