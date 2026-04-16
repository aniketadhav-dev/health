from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database Setup - Fixed: create_engine use hota hai
DATABASE_URL = "sqlite:///./healthcare.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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

# Tables Create karna
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# Seed Doctors data
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
    # Raw SQL ko handle karne ke liye simple query use kar rahe hain
    results = db.query(Appointment, Doctor).join(Doctor, Appointment.doctor_id == Doctor.id).all()
    return [
        {
            "id": a.id,
            "patient_name": a.patient_name,
            "date": a.date,
            "status": a.status,
            "doc_name": d.name
        } for a, d in results
    ]

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
