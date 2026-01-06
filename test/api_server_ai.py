from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uvicorn

# Создаем базу данных SQLite в файле (можно заменить на память :memory:)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Модель для таблицы в БД
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="pending")

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Pydantic модель для API
class TaskCreate(BaseModel):
    title: str
    description: str = ""

class TaskResponse(TaskCreate):
    id: int
    status: str

# FastAPI приложение
app = FastAPI(title="Local Task API")

@app.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate):
    db = SessionLocal()
    db_task = TaskDB(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task

@app.get("/tasks/", response_model=list[TaskResponse])
def read_tasks():
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    db.close()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int):
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    db.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

if __name__ == "__main__":
    # Запуск сервера на http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)