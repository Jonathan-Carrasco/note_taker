from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from services.session_note_service import SessionNoteService
from services.patient_service import PatientService
from services.clinic_service import ClinicService
from services.bcba_service import BcbaService
from models.session_note import SessionNote
from models.patient import Patient
from models.clinic import Clinic
from models.bcba import Bcba
from note_taker_service import NoteTaker

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class CreateSessionNoteRequest(BaseModel):
    bcba: int
    patient_id: int
    clinic_id: Optional[int] = None
    apt_date: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in minutes
    notes: Optional[str] = None

class EditSessionNoteRequest(BaseModel):
    bcba: Optional[int] = None
    patient_id: Optional[int] = None
    clinic_id: Optional[int] = None
    apt_date: Optional[datetime] = None
    duration: Optional[int] = None  # Duration in minutes
    notes: Optional[str] = None

class CreatePatientRequest(BaseModel):
    first_name: str
    last_name: str
    DOB: datetime
    ICD: Optional[str] = None
    address: Optional[str] = None

class CreateBcbaRequest(BaseModel):
    name: str

class LLMQueryRequest(BaseModel):
    observations: str
    model_type: Optional[str] = "openai"
    model_id: Optional[str] = "gpt-4o-2024-05-13"
    api_key: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@app.get("/")
async def health_check():
    return {"status": "healthy"}

# Session Notes endpoints
@app.get("/api/session-notes")
async def get_session_notes_by_bcba(bcba_id: int = Query(..., description="BCBA ID to filter session notes")):
    """Get all session notes for a specific BCBA with patient and clinic details"""
    try:
        result = SessionNoteService().get_by_bcba_with_details(bcba_id)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session notes: {str(e)}")

@app.get("/api/session-notes/{note_id}")
async def get_session_note_by_id(note_id: int):
    """Get a specific session note by ID with patient and clinic details"""
    try:
        result = SessionNoteService().get_by_id_with_details(note_id)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session note: {str(e)}")

@app.post("/api/session-notes")
async def add_session_note(request: CreateSessionNoteRequest):
    """Add a new session note"""
    try:
        result = SessionNoteService().create_with_validation(
            bcba=request.bcba,
            patient_id=request.patient_id,
            notes=request.notes,
            clinic_id=request.clinic_id,
            apt_date=request.apt_date,
            duration=request.duration
        )
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session note: {str(e)}")

@app.put("/api/session-notes/{note_id}")
async def edit_session_note(note_id: int, request: EditSessionNoteRequest):
    """Edit an existing session note"""
    try:
        # Get the existing note first
        existing_result = SessionNoteService().get_by_id(note_id)
        if not existing_result.success:
            return existing_result.to_response()
        
        existing_note = existing_result.data
        
        # Update only provided fields
        updated_note = SessionNote(
            id=note_id,
            bcba=request.bcba if request.bcba is not None else existing_note.bcba,
            patient=request.patient_id if request.patient_id is not None else existing_note.patient,
            clinic=request.clinic_id if request.clinic_id is not None else existing_note.clinic,
            apt_date=request.apt_date if request.apt_date is not None else existing_note.apt_date,
            duration=request.duration if request.duration is not None else existing_note.duration,
            notes=request.notes if request.notes is not None else existing_note.notes
        )
        
        result = SessionNoteService().update(note_id, updated_note)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit session note: {str(e)}")

@app.delete("/api/session-notes/{note_id}")
async def delete_session_note(note_id: int):
    """Delete a session note"""
    try:
        result = SessionNoteService().delete(note_id)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session note: {str(e)}")

# Patients endpoints
@app.get("/api/patients")
async def get_all_patients():
    """Get all patients"""
    try:
        result = PatientService().get_all()
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patients: {str(e)}")

@app.post("/api/patients")
async def create_patient(request: CreatePatientRequest):
    """Create a new patient"""
    try:
        patient = Patient(
            first_name=request.first_name,
            last_name=request.last_name,
            DOB=request.DOB.date(),  # Convert datetime to date
            ICD=request.ICD,
            address=request.address
        )
        result = PatientService().create(patient)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")

# Clinics endpoints
@app.get("/api/clinics")
async def get_all_clinics():
    """Get all clinics"""
    try:
        result = ClinicService().get_all()
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clinics: {str(e)}")

# BCBAs endpoints
@app.get("/api/bcbas")
async def get_all_bcbas():
    """Get all BCBAs"""
    try:
        result = BcbaService().get_all()
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get BCBAs: {str(e)}")

@app.post("/api/bcbas")
async def create_bcba(request: CreateBcbaRequest):
    """Create a new BCBA"""
    try:
        bcba = Bcba(name=request.name)
        result = BcbaService().create(bcba)
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create BCBA: {str(e)}")

@app.post("/api/llm")
async def call_llm(request: LLMQueryRequest):
    """Call LLM with query string to generate notes"""
    try:
        result = NoteTaker().process_request(request.dict())
        return result.to_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to call LLM: {str(e)}")