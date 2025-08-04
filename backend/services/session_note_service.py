from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from sqlite_repository import BaseSQLiteRepository, BaseSQLiteService
from models.session_note import SessionNote
from utils.singleton import SingletonMeta
import database
from utils.result import Result
from .patient_service import PatientService
from .clinic_service import ClinicService
from .bcba_service import BcbaService

class SessionNoteService(BaseSQLiteService[SessionNote], metaclass=SingletonMeta):
    def __init__(self):
        repository = BaseSQLiteRepository(database.session_notes, SessionNote)
        super().__init__(repository)
    
    def create_with_validation(self, bcba: int, patient_id: int, notes: str, 
                             clinic_id: Optional[int] = None, apt_date: Optional[datetime] = None,
                             duration: Optional[int] = None) -> Result:
        """
        Create a session note with foreign key validation
        """
        # Validate BCBA exists
        bcba_result = BcbaService().get_by_id(bcba)
        if not bcba_result.success:
            return Result.error_result(f"BCBA with ID {bcba} does not exist", 400)
        
        # Validate patient exists
        patient_result = PatientService().get_by_id(patient_id)
        if not patient_result.success:
            return Result.error_result(f"Patient with ID {patient_id} does not exist", 400)
        
        # Validate clinic exists if provided
        if clinic_id is not None:
            clinic_result = ClinicService().get_by_id(clinic_id)
            if not clinic_result.success:
                return Result.error_result(f"Clinic with ID {clinic_id} does not exist", 400)
        
        # Create session note
        session_note = SessionNote(
            bcba=bcba,
            patient=patient_id,
            clinic=clinic_id,
            apt_date=apt_date or datetime.now(tz=timezone.utc),
            duration=duration,
            notes=notes
        )
        
        return self.create(session_note)
    
    def get_by_bcba(self, bcba_id: int) -> Result:
        """Get all session notes for a specific BCBA"""
        try:
            from sqlalchemy import select
            
            stmt = select(self.repository.table).where(self.repository.table.c.bcba == bcba_id)
            
            with database.engine.connect() as conn:
                results = conn.execute(stmt).fetchall()
                models = [self.repository._row_to_model(row) for row in results]
                return Result.success_result(models)
                
        except Exception as e:
            return Result.error_result(f"Error fetching session notes for BCBA {bcba_id}: {str(e)}", 500)
    
    def get_by_bcba_with_details(self, bcba_id: int) -> Result:
        """Get all session notes for a specific BCBA with patient, clinic, and BCBA details"""
        try:
            from sqlalchemy import select
            
            notes_table = database.session_notes
            patients_table = database.patients
            clinics_table = database.clinics
            bcbas_table = database.bcbas
            
            # Build query with LEFT JOINs including BCBA
            stmt = select(
                notes_table,
                patients_table.c.first_name.label('patient_first_name'),
                patients_table.c.last_name.label('patient_last_name'),
                clinics_table.c.name.label('clinic_name'),
                bcbas_table.c.name.label('bcba_name')
            ).select_from(
                notes_table.join(patients_table, notes_table.c.patient == patients_table.c.id)
                           .join(clinics_table, notes_table.c.clinic == clinics_table.c.id, isouter=True)
                           .join(bcbas_table, notes_table.c.bcba == bcbas_table.c.id)
            ).where(notes_table.c.bcba == bcba_id)
            
            with database.engine.connect() as conn:
                results = conn.execute(stmt).fetchall()
                
                # Convert results to dictionary format with additional details
                notes_with_details = []
                for row in results:
                    note_dict = {
                        'id': row.id,
                        'bcba': row.bcba,
                        'patient': row.patient,
                        'clinic': row.clinic,
                        'apt_date': row.apt_date.isoformat() if row.apt_date else None,
                        'duration': row.duration,
                        'notes': row.notes,
                        'patient_name': f"{row.patient_first_name} {row.patient_last_name}",
                        'clinic_name': row.clinic_name if row.clinic_name else 'No Clinic',
                        'bcba_name': row.bcba_name
                    }
                    notes_with_details.append(note_dict)
                
                return Result.success_result(notes_with_details)
                
        except Exception as e:
            return Result.error_result(f"Error fetching session notes with details for BCBA {bcba_id}: {str(e)}", 500)
    
    def get_by_id_with_details(self, note_id: int) -> Result:
        """Get a specific session note with patient, clinic, and BCBA details"""
        try:
            from sqlalchemy import select
            
            notes_table = database.session_notes
            patients_table = database.patients
            clinics_table = database.clinics
            bcbas_table = database.bcbas
            
            # Build query with LEFT JOINs including BCBA
            stmt = select(
                notes_table,
                patients_table.c.first_name.label('patient_first_name'),
                patients_table.c.last_name.label('patient_last_name'),
                clinics_table.c.name.label('clinic_name'),
                bcbas_table.c.name.label('bcba_name')
            ).select_from(
                notes_table.join(patients_table, notes_table.c.patient == patients_table.c.id)
                           .join(clinics_table, notes_table.c.clinic == clinics_table.c.id, isouter=True)
                           .join(bcbas_table, notes_table.c.bcba == bcbas_table.c.id)
            ).where(notes_table.c.id == note_id)
            
            with database.engine.connect() as conn:
                result = conn.execute(stmt).fetchone()
                
                if not result:
                    return Result.error_result(f"Session note with ID {note_id} not found", 404)
                
                # Convert result to dictionary format with additional details
                note_with_details = {
                    'id': result.id,
                    'bcba': result.bcba,
                    'patient': result.patient,
                    'clinic': result.clinic,
                    'apt_date': result.apt_date.isoformat() if result.apt_date else None,
                    'duration': result.duration,
                    'notes': result.notes,
                    'patient_name': f"{result.patient_first_name} {result.patient_last_name}",
                    'clinic_name': result.clinic_name if result.clinic_name else 'No Clinic',
                    'bcba_name': result.bcba_name
                }
                
                return Result.success_result(note_with_details)
                
        except Exception as e:
            return Result.error_result(f"Error fetching session note with details for ID {note_id}: {str(e)}", 500) 