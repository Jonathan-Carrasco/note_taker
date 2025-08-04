# ABA Session Notes - Testing Suite

This directory contains the comprehensive test suite for the ABA Session Notes application, including unit tests, integration tests, and a fake data generator.

## 🧪 Test Structure

```
tests/
├── conftest.py           # pytest configuration and fixtures
├── test_session_notes.py # Main CRUD operation tests
└── README.md            # This file

../
├── generate_fake_data.py # Fake data generator
└── run_tests.py         # Test runner script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
# Simple test run
python run_tests.py

# Verbose output
python run_tests.py --verbose

# With coverage report
python run_tests.py --coverage
```

### 3. Generate Fake Data

```bash
# Generate default amounts (15 patients, 5 clinics, 50 notes)
python generate_fake_data.py

# Custom amounts
python generate_fake_data.py --patients 25 --clinics 10 --notes 100
```

## 📋 Test Categories

### **Session Note Creation Tests**

- ✅ Create notes with all fields
- ✅ Create notes without optional fields (clinic, duration)
- ✅ Create notes with default timestamps
- ✅ Foreign key validation (patient/clinic existence)
- ✅ Error handling for invalid data

### **Session Note Retrieval Tests**

- ✅ Get notes by ID
- ✅ Get notes by BCBA ID
- ✅ Get notes with patient/clinic details
- ✅ Handle non-existent records
- ✅ Empty result sets

### **Session Note Update Tests**

- ✅ Update notes content
- ✅ Update duration and timestamps
- ✅ Update all fields individually
- ✅ Handle non-existent records
- ✅ Validation of updated data

### **Session Note Deletion Tests**

- ✅ Delete existing notes
- ✅ Handle non-existent records
- ✅ Verify complete removal

### **Edge Cases & Integration**

- ✅ Empty notes content
- ✅ Very long notes (5000+ characters)
- ✅ Zero duration sessions
- ✅ Multiple notes with same timestamp
- ✅ Complete CRUD workflows
- ✅ Multiple BCBAs and patients

## 🎯 Test Features

### **Isolated Testing**

Each test runs with a fresh, temporary SQLite database to ensure complete isolation and prevent test interference.

### **Realistic Fixtures**

Pre-configured test data including:

- Sample patients with realistic data
- Sample clinics
- Sample session notes
- Multiple patients/notes for complex scenarios

### **Comprehensive Coverage**

- **Unit Tests**: Test individual service methods
- **Integration Tests**: Test complete workflows
- **Edge Cases**: Test boundary conditions and error scenarios
- **Validation Tests**: Test foreign key constraints and data validation

## 📊 Fake Data Generator

The `generate_fake_data.py` script creates realistic ABA therapy data:

### **Features**

- **Realistic Patient Data**: Ages 2-18, appropriate ICD codes, realistic names/addresses
- **Professional Clinic Names**: ABA-specific clinic names and addresses
- **Authentic Session Notes**: Uses ABA therapy templates with realistic content
- **UTC Timestamps**: Proper timezone handling for session dates
- **Random Scheduling**: Sessions scheduled during business hours over the last 6 months

### **Generated Data Types**

**Patients:**

- Realistic names (using Faker library)
- Ages appropriate for ABA therapy (2-18 years)
- Autism spectrum and ADHD ICD codes
- Complete addresses

**Clinics:**

- Professional ABA therapy center names
- Realistic addresses in various locations

**Session Notes:**

- Multiple professional note templates covering:
  - Communication goals
  - Social skills development
  - Behavioral interventions
  - Academic readiness
  - Play-based interventions
- Realistic data including trial counts, accuracy percentages, intervention strategies
- Session durations (30-120 minutes)
- Multiple BCBA IDs (101-105)

### **Usage Examples**

```bash
# Quick test data
python generate_fake_data.py --patients 5 --clinics 2 --notes 20

# Large dataset for performance testing
python generate_fake_data.py --patients 100 --clinics 15 --notes 500

# Default realistic dataset
python generate_fake_data.py
```

## 🔧 Running Specific Tests

### **Run Only Creation Tests**

```bash
python -m pytest tests/test_session_notes.py::TestSessionNoteCreation -v
```

### **Run Only CRUD Tests**

```bash
python -m pytest tests/test_session_notes.py::TestSessionNoteRetrieval -v
python -m pytest tests/test_session_notes.py::TestSessionNoteUpdating -v
python -m pytest tests/test_session_notes.py::TestSessionNoteDeletion -v
```

### **Run Integration Tests**

```bash
python -m pytest tests/test_session_notes.py::TestSessionNoteIntegration -v
```

### **Run with Coverage Report**

```bash
python -m pytest --cov=. --cov-report=html tests/
```

## 🛠️ Test Configuration

### **Environment Variables**

Tests automatically handle database configuration - no environment setup required.

### **Database Isolation**

Each test function gets a fresh temporary database, ensuring complete isolation.

### **Fixtures Available**

- `temp_database`: Temporary test database
- `sample_patient`: Single test patient
- `sample_clinic`: Single test clinic
- `sample_session_note`: Single test session note
- `multiple_patients`: Multiple test patients
- `multiple_session_notes`: Multiple test session notes

## 🐛 Debugging Tests

### **Verbose Output**

```bash
python run_tests.py --verbose
```

### **Run Single Test**

```bash
python -m pytest tests/test_session_notes.py::TestSessionNoteCreation::test_create_session_note_with_all_fields -v -s
```

### **Print Debug Information**

Add `print()` statements in tests and run with `-s` flag to see output.

## 🔄 Continuous Integration

The test suite is designed to be CI/CD friendly:

- No external dependencies (uses temporary SQLite databases)
- Fast execution (typically under 30 seconds)
- Clear pass/fail indicators
- Detailed error reporting

## 📝 Adding New Tests

1. **Create test methods** in appropriate test classes
2. **Use existing fixtures** or create new ones in `conftest.py`
3. **Follow naming convention**: `test_<functionality>_<scenario>`
4. **Include assertions** using helper functions like `assert_result_success()`
5. **Add docstrings** explaining what the test validates

Example:

```python
def test_create_session_note_custom_scenario(self, sample_patient):
    """Test creating a session note with custom scenario"""
    result = SessionNoteService.instance().create_with_validation(
        bcba=123,
        patient_id=sample_patient.id,
        notes="Custom test scenario"
    )

    assert_result_success(result, "Should create note with custom scenario")
    # Add more specific assertions...
```

## 🎉 Ready to Test!

Your test suite is comprehensive and ready to ensure the reliability of your ABA Session Notes application. Run the tests regularly during development and before deploying changes.
