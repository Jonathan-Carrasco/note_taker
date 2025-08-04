"""
pytest configuration and fixtures for ABA Session Notes tests
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, String, Date, DateTime, ForeignKey
from models.patient import Patient
from models.clinic import Clinic
from models.session_note import SessionNote
from models.bcba import Bcba
from services.patient_service import PatientService
from services.clinic_service import ClinicService
from services.session_note_service import SessionNoteService
from services.bcba_service import BcbaService
from utils.singleton import SingletonMeta
import database

@pytest.fixture(scope="function")
def temp_database():
    """Create a temporary test database for each test"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)  # Close the file descriptor immediately
    
    # Store original values
    original_path = database.DATABASE_PATH
    original_url = database.DATABASE_URL
    original_engine = database.engine
    original_metadata = database.metadata
    original_patients = database.patients
    original_clinics = database.clinics
    original_session_notes = database.session_notes
    original_bcbas = database.bcbas
    
    try:
        # Override the database settings
        database.DATABASE_PATH = db_path
        database.DATABASE_URL = f'sqlite:///{db_path}'
        
        # Create new engine with test database
        database.engine = create_engine(database.DATABASE_URL, echo=False)
        database.metadata = MetaData()
        
        # Recreate table definitions for test database
        database.bcbas = Table(
            'bcbas',
            database.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', Text, nullable=False)
        )
        
        database.patients = Table(
            'patients',
            database.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('first_name', Text, nullable=False),
            Column('last_name', Text, nullable=False),
            Column('DOB', Date, nullable=False),
            Column('ICD', String(15), nullable=True),
            Column('address', Text, nullable=True)
        )
        
        database.clinics = Table(
            'clinics',
            database.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', Text, nullable=False),
            Column('address', Text, nullable=True)
        )
        
        database.session_notes = Table(
            'session_notes',
            database.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('bcba', Integer, ForeignKey('bcbas.id'), nullable=False),
            Column('patient', Integer, ForeignKey('patients.id'), nullable=False),
            Column('clinic', Integer, ForeignKey('clinics.id'), nullable=True),
            Column('apt_date', DateTime, nullable=False),
            Column('duration', Integer, nullable=True),
            Column('notes', Text, nullable=True)
        )
        
        # Create all tables
        database.metadata.create_all(database.engine)
        
        # Clear singleton instances to force them to use new database
        SingletonMeta._instances.clear()
        
        yield db_path
        
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except FileNotFoundError:
            pass
        
        # Restore original database settings
        database.DATABASE_PATH = original_path
        database.DATABASE_URL = original_url
        database.engine = original_engine
        database.metadata = original_metadata
        database.patients = original_patients
        database.clinics = original_clinics
        database.session_notes = original_session_notes
        database.bcbas = original_bcbas
        
        # Clear singleton instances again to reset to original database
        SingletonMeta._instances.clear()

@pytest.fixture
def sample_bcba(temp_database):
    """Create a sample BCBA for testing"""
    bcba = Bcba(name="Dr. Test BCBA")
    
    result = BcbaService().create(bcba)
    if result.success:
        bcba.id = result.data
        return bcba
    else:
        pytest.fail(f"Failed to create sample BCBA: {result.error}")

@pytest.fixture
def sample_patient(temp_database):
    """Create a sample patient for testing"""
    patient = Patient(
        first_name="John",
        last_name="Doe",
        DOB=datetime(2015, 1, 1).date(),
        ICD="F84.0",
        address="123 Test Street, Test City, ST 12345"
    )
    
    result = PatientService().create(patient)
    if result.success:
        patient.id = result.data
        return patient
    else:
        pytest.fail(f"Failed to create sample patient: {result.error}")

@pytest.fixture
def sample_clinic(temp_database):
    """Create a sample clinic for testing"""
    clinic = Clinic(
        name="Test ABA Clinic",
        address="456 Clinic Ave, Test City, ST 12345"
    )
    
    result = ClinicService().create(clinic)
    if result.success:
        clinic.id = result.data
        return clinic
    else:
        pytest.fail(f"Failed to create sample clinic: {result.error}")

@pytest.fixture
def sample_session_note(temp_database, sample_bcba, sample_patient, sample_clinic):
    """Create a sample session note for testing"""
    session_date = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    
    result = SessionNoteService().create_with_validation(
        bcba=sample_bcba.id,
        patient_id=sample_patient.id,
        clinic_id=sample_clinic.id,
        apt_date=session_date,
        duration=60,
        notes="Test session note for patient. Worked on communication goals."
    )
    
    if result.success:
        # Get the created note
        note_result = SessionNoteService().get_by_id(result.data)
        if note_result.success:
            return note_result.data
        else:
            pytest.fail(f"Failed to retrieve created session note: {note_result.error}")
    else:
        pytest.fail(f"Failed to create sample session note: {result.error}")

@pytest.fixture
def multiple_patients(temp_database):
    """Create multiple patients for testing"""
    patients = []
    patient_data = [
        ("Alice", "Smith", datetime(2010, 5, 15).date(), "F84.1"),
        ("Bob", "Johnson", datetime(2012, 8, 20).date(), "F84.0"),
        ("Carol", "Williams", datetime(2014, 3, 10).date(), "F90.0")
    ]
    
    for first_name, last_name, dob, icd in patient_data:
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            DOB=dob,
            ICD=icd,
            address=f"Address for {first_name} {last_name}"
        )
        
        result = PatientService().create(patient)
        if result.success:
            patient.id = result.data
            patients.append(patient)
        else:
            pytest.fail(f"Failed to create patient {first_name} {last_name}: {result.error}")
    
    return patients

@pytest.fixture
def multiple_bcbas(temp_database):
    """Create multiple BCBAs for testing"""
    bcbas = []
    bcba_names = ["Dr. Test BCBA 1", "Dr. Test BCBA 2", "Dr. Test BCBA 3"]
    
    for name in bcba_names:
        bcba = Bcba(name=name)
        
        result = BcbaService().create(bcba)
        if result.success:
            bcba.id = result.data
            bcbas.append(bcba)
        else:
            pytest.fail(f"Failed to create BCBA {name}: {result.error}")
    
    return bcbas

@pytest.fixture
def multiple_session_notes(temp_database, sample_patient, sample_clinic, multiple_bcbas):
    """Create multiple session notes for testing"""
    notes = []
    
    for i, bcba in enumerate(multiple_bcbas):
        session_date = datetime(2025, 1, i+1, 10 + i, 0, 0, tzinfo=timezone.utc)
        
        result = SessionNoteService().create_with_validation(
            bcba=bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id if i % 2 == 0 else None,  # Alternate clinic assignment
            apt_date=session_date,
            duration=60 + (i * 15),  # Varying durations
            notes=f"Test session note #{i+1} for BCBA {bcba.name}. Patient made progress."
        )
        
        if result.success:
            note_result = SessionNoteService().get_by_id(result.data)
            if note_result.success:
                notes.append(note_result.data)
            else:
                pytest.fail(f"Failed to retrieve created session note: {note_result.error}")
        else:
            pytest.fail(f"Failed to create session note {i+1}: {result.error}")
    
    return notes

# Helper functions for tests
def assert_result_success(result, message="Operation should succeed"):
    """Assert that a Result object indicates success"""
    assert result.success, f"{message}. Error: {result.error}"

def assert_result_error(result, message="Operation should fail"):
    """Assert that a Result object indicates failure"""
    assert not result.success, f"{message}. Expected failure but got success." 