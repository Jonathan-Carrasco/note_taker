"""
Tests for Session Notes CRUD operations

This test suite covers:
- Creating session notes
- Reading session notes (by ID and by BCBA)
- Updating session notes
- Deleting session notes
- Foreign key validation (including BCBA validation)
- Edge cases and error handling
"""

from datetime import datetime, timezone
from services.session_note_service import SessionNoteService
from models.session_note import SessionNote
from conftest import assert_result_success, assert_result_error

class TestSessionNoteCreation:
    """Test session note creation functionality"""
    
    def test_create_session_note_with_all_fields(self, sample_bcba, sample_patient, sample_clinic):
        """Test creating a session note with all fields populated"""
        session_date = datetime(2025, 2, 1, 14, 30, 0, tzinfo=timezone.utc)
        notes_content = "Patient demonstrated excellent progress in communication skills today."
        
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            apt_date=session_date,
            duration=75,
            notes=notes_content
        )
        
        assert_result_success(result, "Should create session note with all fields")
        note_id = result.data
        assert note_id is not None
        assert isinstance(note_id, int)
        
        # Verify the note was created correctly
        get_result = SessionNoteService().get_by_id(note_id)
        assert_result_success(get_result, "Should retrieve created note")
        
        created_note = get_result.data
        assert created_note.bcba == sample_bcba.id
        assert created_note.patient == sample_patient.id
        assert created_note.clinic == sample_clinic.id
        # Compare dates without timezone info since SQLite stores naive datetimes
        assert created_note.apt_date.replace(tzinfo=timezone.utc) == session_date
        assert created_note.duration == 75
        assert created_note.notes == notes_content
    
    def test_create_session_note_without_clinic(self, sample_bcba, sample_patient):
        """Test creating a session note without a clinic (optional field)"""
        session_date = datetime(2025, 2, 2, 9, 0, 0, tzinfo=timezone.utc)
        
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=None,
            apt_date=session_date,
            duration=60,
            notes="Home-based session. Patient worked on self-help skills."
        )
        
        assert_result_success(result, "Should create session note without clinic")
        
        # Verify clinic is None
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        assert get_result.data.clinic is None
    
    def test_create_session_note_without_duration(self, sample_bcba, sample_patient, sample_clinic):
        """Test creating a session note without duration (optional field)"""
        session_date = datetime(2025, 2, 3, 11, 15, 0, tzinfo=timezone.utc)
        
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            apt_date=session_date,
            duration=None,
            notes="Session completed. Duration not recorded."
        )
        
        assert_result_success(result, "Should create session note without duration")
        
        # Verify duration is None
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        assert get_result.data.duration is None
    
    def test_create_session_note_with_default_date(self, sample_bcba, sample_patient):
        """Test creating a session note with default date (current UTC time)"""
        before_creation = datetime.now(timezone.utc)
        
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            notes="Session with default timestamp."
        )
        
        after_creation = datetime.now(timezone.utc)
        assert_result_success(result, "Should create session note with default date")
        
        # Verify the date is between our before/after timestamps
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        
        note_date = get_result.data.apt_date.replace(tzinfo=timezone.utc)
        assert before_creation <= note_date <= after_creation
    
    def test_create_session_note_invalid_bcba(self, sample_patient, sample_clinic):
        """Test creating a session note with non-existent BCBA ID"""
        result = SessionNoteService().create_with_validation(
            bcba=99999,  # Non-existent BCBA ID
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            notes="This should fail due to invalid BCBA."
        )
        
        assert_result_error(result, "Should fail with invalid BCBA ID")
        assert "BCBA with ID 99999 does not exist" in result.error
    
    def test_create_session_note_invalid_patient(self, sample_bcba, sample_clinic):
        """Test creating a session note with non-existent patient ID"""
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=99999,  # Non-existent patient ID
            clinic_id=sample_clinic.id,
            notes="This should fail due to invalid patient."
        )
        
        assert_result_error(result, "Should fail with invalid patient ID")
        assert "Patient with ID 99999 does not exist" in result.error
    
    def test_create_session_note_invalid_clinic(self, sample_bcba, sample_patient):
        """Test creating a session note with non-existent clinic ID"""
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=99999,  # Non-existent clinic ID
            notes="This should fail due to invalid clinic."
        )
        
        assert_result_error(result, "Should fail with invalid clinic ID")
        assert "Clinic with ID 99999 does not exist" in result.error

class TestSessionNoteRetrieval:
    """Test session note retrieval functionality"""
    
    def test_get_session_note_by_id(self, sample_session_note):
        """Test retrieving a session note by its ID"""
        result = SessionNoteService().get_by_id(sample_session_note.id)
        
        assert_result_success(result, "Should retrieve session note by ID")
        retrieved_note = result.data
        
        assert retrieved_note.id == sample_session_note.id
        assert retrieved_note.bcba == sample_session_note.bcba
        assert retrieved_note.notes == sample_session_note.notes
    
    def test_get_nonexistent_session_note(self, temp_database):
        """Test retrieving a session note that doesn't exist"""
        result = SessionNoteService().get_by_id(99999)
        
        assert_result_error(result, "Should fail to retrieve non-existent note")
        assert result.status_code == 404
    
    def test_get_session_notes_by_bcba(self, multiple_session_notes, multiple_bcbas):
        """Test retrieving session notes filtered by BCBA ID"""
        # Get notes for the first BCBA
        first_bcba = multiple_bcbas[0]
        result = SessionNoteService().get_by_bcba(first_bcba.id)
        
        assert_result_success(result, "Should retrieve notes by BCBA")
        notes = result.data
        assert isinstance(notes, list)
        
        # Should have exactly one note for this BCBA
        bcba_notes = [note for note in notes if note.bcba == first_bcba.id]
        assert len(bcba_notes) == 1
        assert bcba_notes[0].bcba == first_bcba.id
    
    def test_get_session_notes_by_bcba_with_details(self, multiple_session_notes, multiple_bcbas, sample_patient, sample_clinic):
        """Test retrieving session notes with patient, clinic, and BCBA details"""
        first_bcba = multiple_bcbas[0]
        result = SessionNoteService().get_by_bcba_with_details(first_bcba.id)
        
        assert_result_success(result, "Should retrieve notes with details")
        notes_with_details = result.data
        assert isinstance(notes_with_details, list)
        assert len(notes_with_details) > 0
        
        # Check that patient, clinic, and BCBA names are included
        note_detail = notes_with_details[0]
        assert 'patient_name' in note_detail
        assert 'clinic_name' in note_detail
        assert 'bcba_name' in note_detail
        assert note_detail['patient_name'] == f"{sample_patient.first_name} {sample_patient.last_name}"
        assert note_detail['bcba_name'] == first_bcba.name
    
    def test_get_session_notes_empty_bcba(self, temp_database):
        """Test retrieving session notes for BCBA with no notes"""
        result = SessionNoteService().get_by_bcba(99999)
        
        assert_result_success(result, "Should succeed with empty list for unknown BCBA")
        notes = result.data
        assert isinstance(notes, list)
        assert len(notes) == 0

class TestSessionNoteUpdating:
    """Test session note updating functionality"""
    
    def test_update_session_note_notes_field(self, sample_session_note):
        """Test updating the notes field of a session note"""
        original_notes = sample_session_note.notes
        new_notes = "Updated: Patient showed significant improvement in all target areas."
        
        # Create updated note object
        updated_note = SessionNote(
            id=sample_session_note.id,
            bcba=sample_session_note.bcba,
            patient=sample_session_note.patient,
            clinic=sample_session_note.clinic,
            apt_date=sample_session_note.apt_date,
            duration=sample_session_note.duration,
            notes=new_notes
        )
        
        result = SessionNoteService().update(sample_session_note.id, updated_note)
        assert_result_success(result, "Should update session note")
        
        # Verify the update
        get_result = SessionNoteService().get_by_id(sample_session_note.id)
        assert_result_success(get_result)
        retrieved_note = get_result.data
        
        assert retrieved_note.notes == new_notes
        assert retrieved_note.notes != original_notes
    
    def test_update_session_note_duration(self, sample_session_note):
        """Test updating the duration of a session note"""
        new_duration = 90
        
        updated_note = SessionNote(
            id=sample_session_note.id,
            bcba=sample_session_note.bcba,
            patient=sample_session_note.patient,
            clinic=sample_session_note.clinic,
            apt_date=sample_session_note.apt_date,
            duration=new_duration,
            notes=sample_session_note.notes
        )
        
        result = SessionNoteService().update(sample_session_note.id, updated_note)
        assert_result_success(result, "Should update session note duration")
        
        # Verify the update
        get_result = SessionNoteService().get_by_id(sample_session_note.id)
        assert_result_success(get_result)
        assert get_result.data.duration == new_duration
    
    def test_update_session_note_datetime(self, sample_session_note):
        """Test updating the appointment date/time of a session note"""
        new_date = datetime(2025, 3, 15, 14, 30, 0, tzinfo=timezone.utc)
        
        updated_note = SessionNote(
            id=sample_session_note.id,
            bcba=sample_session_note.bcba,
            patient=sample_session_note.patient,
            clinic=sample_session_note.clinic,
            apt_date=new_date,
            duration=sample_session_note.duration,
            notes=sample_session_note.notes
        )
        
        result = SessionNoteService().update(sample_session_note.id, updated_note)
        assert_result_success(result, "Should update session note date/time")
        
        # Verify the update
        get_result = SessionNoteService().get_by_id(sample_session_note.id)
        assert_result_success(get_result)
        assert get_result.data.apt_date.replace(tzinfo=timezone.utc) == new_date
    
    def test_update_nonexistent_session_note(self, temp_database):
        """Test updating a session note that doesn't exist"""
        fake_note = SessionNote(
            id=99999,
            bcba=1,
            patient=1,
            clinic=1,
            apt_date=datetime.now(timezone.utc),
            duration=60,
            notes="This should fail"
        )
        
        result = SessionNoteService().update(99999, fake_note)
        assert_result_error(result, "Should fail to update non-existent note")

class TestSessionNoteDeletion:
    """Test session note deletion functionality"""
    
    def test_delete_session_note(self, sample_session_note):
        """Test deleting a session note"""
        note_id = sample_session_note.id
        
        # Verify note exists before deletion
        get_result = SessionNoteService().get_by_id(note_id)
        assert_result_success(get_result, "Note should exist before deletion")
        
        # Delete the note
        delete_result = SessionNoteService().delete(note_id)
        assert_result_success(delete_result, "Should delete session note")
        
        # Verify note no longer exists
        get_result_after = SessionNoteService().get_by_id(note_id)
        assert_result_error(get_result_after, "Note should not exist after deletion")
        assert get_result_after.status_code == 404
    
    def test_delete_nonexistent_session_note(self, temp_database):
        """Test deleting a session note that doesn't exist"""
        result = SessionNoteService().delete(99999)
        assert_result_error(result, "Should fail to delete non-existent note")
        assert result.status_code == 404

class TestSessionNoteEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_create_session_note_with_empty_notes(self, sample_bcba, sample_patient):
        """Test creating a session note with empty notes field"""
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            notes=""  # Empty notes
        )
        
        assert_result_success(result, "Should allow empty notes")
        
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        assert get_result.data.notes == ""
    
    def test_create_session_note_with_very_long_notes(self, sample_bcba, sample_patient):
        """Test creating a session note with very long notes content"""
        long_notes = "A" * 5000  # Very long notes
        
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            notes=long_notes
        )
        
        assert_result_success(result, "Should handle long notes")
        
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        assert get_result.data.notes == long_notes
    
    def test_create_session_note_with_zero_duration(self, sample_bcba, sample_patient):
        """Test creating a session note with zero duration"""
        result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            duration=0,
            notes="Session with zero duration."
        )
        
        assert_result_success(result, "Should allow zero duration")
        
        get_result = SessionNoteService().get_by_id(result.data)
        assert_result_success(get_result)
        assert get_result.data.duration == 0
    
    def test_create_multiple_notes_same_datetime(self, sample_bcba, sample_patient, sample_clinic):
        """Test creating multiple session notes with the same date/time"""
        session_date = datetime(2025, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        
        # Create first note
        result1 = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            apt_date=session_date,
            notes="First session note"
        )
        assert_result_success(result1, "Should create first note")
        
        # Create second note with same datetime (different patient would be more realistic, but for simplicity using same)
        result2 = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            apt_date=session_date,
            notes="Second session note"
        )
        assert_result_success(result2, "Should create second note with same datetime")
        
        # Verify both notes exist
        assert result1.data != result2.data  # Different IDs

class TestSessionNoteIntegration:
    """Integration tests with multiple services"""
    
    def test_complete_workflow_create_update_delete(self, sample_bcba, sample_patient, sample_clinic):
        """Test complete workflow: create, read, update, delete"""
        # 1. Create
        session_date = datetime(2025, 5, 1, 15, 0, 0, tzinfo=timezone.utc)
        
        create_result = SessionNoteService().create_with_validation(
            bcba=sample_bcba.id,
            patient_id=sample_patient.id,
            clinic_id=sample_clinic.id,
            apt_date=session_date,
            duration=60,
            notes="Initial session note for integration test."
        )
        assert_result_success(create_result, "Should create note")
        note_id = create_result.data
        
        # 2. Read
        read_result = SessionNoteService().get_by_id(note_id)
        assert_result_success(read_result, "Should read note")
        original_note = read_result.data
        
        # 3. Update
        updated_note = SessionNote(
            id=note_id,
            bcba=original_note.bcba,
            patient=original_note.patient,
            clinic=original_note.clinic,
            apt_date=original_note.apt_date,
            duration=75,  # Updated duration
            notes="Updated session note for integration test."
        )
        
        update_result = SessionNoteService().update(note_id, updated_note)
        assert_result_success(update_result, "Should update note")
        
        # Verify update
        read_updated_result = SessionNoteService().get_by_id(note_id)
        assert_result_success(read_updated_result, "Should read updated note")
        assert read_updated_result.data.duration == 75
        assert "Updated session note" in read_updated_result.data.notes
        
        # 4. Delete
        delete_result = SessionNoteService().delete(note_id)
        assert_result_success(delete_result, "Should delete note")
        
        # Verify deletion
        read_deleted_result = SessionNoteService().get_by_id(note_id)
        assert_result_error(read_deleted_result, "Should not find deleted note")
    
    def test_multiple_bcbas_multiple_patients(self, multiple_patients, multiple_bcbas, sample_clinic):
        """Test session notes with multiple BCBAs and patients"""
        created_notes = []
        
        # Create notes for each BCBA-patient combination
        for bcba in multiple_bcbas:
            for patient in multiple_patients:
                result = SessionNoteService().create_with_validation(
                    bcba=bcba.id,
                    patient_id=patient.id,
                    clinic_id=sample_clinic.id,
                    notes=f"Note for {bcba.name} and patient {patient.first_name}"
                )
                assert_result_success(result, f"Should create note for {bcba.name}")
                created_notes.append((bcba.id, patient.id, result.data))
        
        # Verify each BCBA has the correct number of notes
        for bcba in multiple_bcbas:
            result = SessionNoteService().get_by_bcba(bcba.id)
            assert_result_success(result, f"Should get notes for {bcba.name}")
            notes = result.data
            assert len(notes) == len(multiple_patients), f"{bcba.name} should have {len(multiple_patients)} notes" 