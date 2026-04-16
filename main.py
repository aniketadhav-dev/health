from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_all, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os

# Database Setup
DATABASE_URL = "sqlite:///./healthcare.db"
Base = declarative_base()
engine = create_all(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialty = Column(String)
    fee = Column(Integer)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    doctor_id = Column(Integer)
    date = Column(String)
    status = Column(String, default="Confirmed")

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# Seed Doctors if empty
@app.on_event("startup")
def seed():
    db = SessionLocal()
    if db.query(Doctor).count() == 0:
        docs = [
            Doctor(name="Dr. Aryan Sharma", specialty="Cardiologist", fee=800),
            Doctor(name="Dr. Sara Khan", specialty="Dermatologist", fee=600),
            Doctor(name="Dr. John Wick", specialty="Surgeon", fee=1200),
            Doctor(name="Dr. Lisa Ray", specialty="Pediatrician", fee=500)
        ]
        db.add_all(docs)
        db.commit()
    db.close()

# API Routes
@app.get("/api/doctors")
def get_doctors(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Doctor)
    if search:
        query = query.filter(Doctor.specialty.contains(search))
    return query.all()

@app.post("/api/book")
def book(data: dict, db: Session = Depends(get_db)):
    new_app = Appointment(patient_name=data['patient'], doctor_id=data['doc_id'], date=data['date'])
    db.add(new_app)
    db.commit()
    return {"message": "Booked"}

@app.get("/api/my-appointments")
def get_apps(db: Session = Depends(get_db)):
    results = db.execute("SELECT a.id, a.patient_name, a.date, a.status, d.name as doc_name FROM appointments a JOIN doctors d ON a.doctor_id = d.id").fetchall()
    return [dict(row) for row in results]

@app.delete("/api/cancel/{id}")
def cancel(id: int, db: Session = Depends(get_db)):
    db.query(Appointment).filter(Appointment.id == id).delete()
    db.commit()
    return {"message": "Cancelled"}

@app.get("/")
def home(): return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
