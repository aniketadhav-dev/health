from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()

# Data Models
class Appointment(BaseModel):
    doctor_name: str
    patient_name: str
    date: str

# In-memory "Database"
doctors = ["Dr. Sharma (Cardio)", "Dr. Verma (Skin)", "Dr. Khanna (General)"]
appointments = []

# API Endpoints
@app.get("/api/doctors")
def get_doctors():
    return doctors

@app.post("/api/book")
def book_appointment(appmt: Appointment):
    appointments.append(appmt.dict())
    return {"message": "Success", "data": appmt}

@app.get("/api/my-appointments")
def get_appointments():
    return appointments

# Serve Frontend
@app.get("/")
async def read_index():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    # Render assigns a port via environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
