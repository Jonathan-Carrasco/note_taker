#!/usr/bin/env python3
"""
Fake Data Generator for ABA Session Notes Application

This script generates realistic fake data for testing and demonstration purposes.
Run this script to populate your database with sample patients, clinics, BCBAs, and session notes.

Usage:
    python generate_fake_data.py [--patients N] [--clinics N] [--bcbas N] [--notes N]
"""

import argparse
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from services.patient_service import PatientService
from services.clinic_service import ClinicService
from services.session_note_service import SessionNoteService
from services.bcba_service import BcbaService
from models.patient import Patient
from models.clinic import Clinic
from models.bcba import Bcba

# Initialize Faker
fake = Faker()

# ABA-specific data
ICD_CODES = [
    "F84.0",  # Autistic disorder
    "F84.1",  # Atypical autism
    "F84.2",  # Rett's disorder
    "F84.3",  # Other childhood disintegrative disorder
    "F84.5",  # Asperger's syndrome
    "F84.8",  # Other pervasive developmental disorders
    "F84.9",  # Pervasive developmental disorder, unspecified
    "F90.0",  # ADHD predominantly inattentive type
    "F90.1",  # ADHD predominantly hyperactive type
    "F90.2",  # ADHD combined type
]

CLINIC_NAMES = [
    "Sunshine ABA Therapy Center",
    "Bright Futures Behavioral Health",
    "Growing Minds ABA Clinic",
    "Rainbow Therapy Services",
    "Little Steps ABA Center",
    "Breakthrough Behavioral Solutions",
    "Caring Hearts Autism Center",
    "New Horizons ABA Therapy",
    "Positive Pathways Clinic",
    "Thrive ABA Services",
    "Harmony Behavioral Health",
    "Excellence in ABA",
    "Hope & Healing Center",
    "Building Blocks ABA",
    "Stepping Stones Therapy"
]

BCBA_NAMES = [
    "Dr. Sarah Johnson, BCBA",
    "Dr. Michael Chen, BCBA", 
    "Dr. Emily Rodriguez, BCBA",
    "Dr. David Thompson, BCBA",
    "Dr. Lisa Park, BCBA",
    "Dr. Jennifer Martinez, BCBA",
    "Dr. Kevin Brown, BCBA",
    "Dr. Amanda Wilson, BCBA",
    "Dr. Robert Taylor, BCBA",
    "Dr. Michelle Davis, BCBA",
    "Dr. Christopher Garcia, BCBA",
    "Dr. Nicole Miller, BCBA",
    "Dr. Steven Anderson, BCBA",
    "Dr. Jessica White, BCBA",
    "Dr. Daniel Lee, BCBA"
]

ABA_NOTE_TEMPLATES = [
    """Patient worked on communication goals during this session. Demonstrated improved eye contact and joint attention skills. Completed {trials} trials of requesting preferred items with {accuracy}% accuracy. Used {prompting} prompting and provided {reinforcement} reinforcement. Patient showed {behavior} throughout the session. Next session will focus on {next_goal}.""",
    
    """Session focused on social skills development. Patient engaged in {activity} for {duration} minutes with minimal prompting. Demonstrated appropriate turn-taking behavior {frequency}. Worked on greeting peers and adults with {success_rate}% independence. {challenging_behavior}. Plan to continue working on social initiation in next session.""",
    
    """Behavioral intervention session completed. Target behaviors: {target_behaviors}. Patient displayed {positive_behaviors} and required intervention for {negative_behaviors}. Used {intervention_strategy} with good results. Data collected shows {progress_note}. Recommend continuing current behavior plan with {modification}.""",
    
    """Academic readiness skills session. Worked on {academic_skill} with {success_level} success. Patient completed {task_count} tasks independently and required assistance with {assistance_areas}. Attention span was {attention_level} lasting approximately {attention_duration} minutes. {additional_notes}.""",
    
    """Play-based intervention session. Patient engaged in {play_activity} and demonstrated {play_skills}. Social engagement improved with {social_improvements}. Motor skills practice included {motor_activities} with {motor_success}. Patient showed {emotional_regulation} emotional regulation throughout session. Next session will incorporate {next_activities}."""
]

def generate_note_content():
    """Generate realistic ABA session note content"""
    template = random.choice(ABA_NOTE_TEMPLATES)
    
    # Fill in template variables with realistic values
    replacements = {
        'trials': random.randint(5, 20),
        'accuracy': random.randint(60, 95),
        'prompting': random.choice(['minimal', 'moderate', 'full physical', 'gestural', 'verbal']),
        'reinforcement': random.choice(['verbal praise', 'preferred items', 'token reinforcement', 'social reinforcement']),
        'behavior': random.choice(['excellent engagement', 'good cooperation', 'some resistance initially', 'high motivation']),
        'next_goal': random.choice(['expressive language', 'receptive language', 'social skills', 'academic readiness']),
        'activity': random.choice(['structured play', 'turn-taking games', 'group activities', 'peer interaction']),
        'duration': random.randint(10, 30),
        'frequency': random.choice(['3/5 opportunities', '4/6 trials', '7/10 attempts', '2/3 instances']),
        'success_rate': random.randint(70, 95),
        'challenging_behavior': random.choice(['No challenging behaviors observed', 'Brief tantrum at transition (2 minutes)', 'Mild attention seeking behavior']),
        'target_behaviors': random.choice(['aggression, non-compliance', 'tantrums, self-stimming', 'attention seeking, disruption']),
        'positive_behaviors': random.choice(['following instructions', 'appropriate communication', 'calm transitions']),
        'negative_behaviors': random.choice(['brief non-compliance', 'attention seeking', 'minimal disruption']),
        'intervention_strategy': random.choice(['positive reinforcement', 'planned ignoring', 'redirection', 'token economy']),
        'progress_note': random.choice(['20% reduction in target behaviors', 'improvement in compliance', 'increased appropriate communication']),
        'modification': random.choice(['slight adjustments', 'increased reinforcement schedule', 'no changes needed']),
        'academic_skill': random.choice(['letter recognition', 'number identification', 'shape sorting', 'color matching']),
        'success_level': random.choice(['high', 'moderate', 'emerging']),
        'task_count': random.randint(3, 10),
        'assistance_areas': random.choice(['fine motor tasks', 'complex instructions', 'sequencing activities']),
        'attention_level': random.choice(['excellent', 'good', 'variable', 'improving']),
        'attention_duration': random.randint(5, 25),
        'additional_notes': random.choice(['Great session overall!', 'Continue current strategies.', 'Consider increasing difficulty.']),
        'play_activity': random.choice(['puzzle completion', 'building blocks', 'pretend play', 'sensory activities']),
        'play_skills': random.choice(['improved sharing', 'better turn-taking', 'increased creativity']),
        'social_improvements': random.choice(['peer interaction', 'eye contact', 'joint attention']),
        'motor_activities': random.choice(['cutting with scissors', 'writing practice', 'ball skills', 'gross motor games']),
        'motor_success': random.choice(['good progress', 'some improvement', 'continued practice needed']),
        'emotional_regulation': random.choice(['excellent', 'good', 'improved', 'variable']),
        'next_activities': random.choice(['new sensory activities', 'advanced social games', 'academic challenges'])
    }
    
    try:
        return template.format(**replacements)
    except KeyError:
        # Fallback if any key is missing
        return f"Session completed successfully. Patient showed good engagement and made progress toward goals. Duration: {random.randint(30, 90)} minutes."

def generate_patients(count: int) -> list:
    """Generate fake patients"""
    print(f"Generating {count} fake patients...")
    patients = []
    
    for i in range(count):
        # Generate age between 2-18 years old
        age_years = random.randint(2, 18)
        birth_date = fake.date_between(
            start_date=f'-{age_years + 1}y',
            end_date=f'-{age_years}y'
        )
        
        patient = Patient(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            DOB=birth_date,
            ICD=random.choice(ICD_CODES),
            address=fake.address().replace('\n', ', ')
        )
        
        result = PatientService().create(patient)
        if result.success:
            patient.id = result.data
            patients.append(patient)
            print(f"  Created patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")
        else:
            print(f"  Failed to create patient: {result.error}")
    
    return patients

def generate_clinics(count: int) -> list:
    """Generate fake clinics"""
    print(f"Generating {count} fake clinics...")
    clinics = []
    
    clinic_names = random.sample(CLINIC_NAMES, min(count, len(CLINIC_NAMES)))
    
    for name in clinic_names:
        clinic = Clinic(
            name=name,
            address=fake.address().replace('\n', ', ')
        )
        
        result = ClinicService().create(clinic)
        if result.success:
            clinic.id = result.data
            clinics.append(clinic)
            print(f"  Created clinic: {clinic.name} (ID: {clinic.id})")
        else:
            print(f"  Failed to create clinic: {result.error}")
    
    return clinics

def generate_bcbas(count: int) -> list:
    """Generate fake BCBAs"""
    print(f"Generating {count} fake BCBAs...")
    bcbas = []
    
    bcba_names = random.sample(BCBA_NAMES, min(count, len(BCBA_NAMES)))
    
    for name in bcba_names:
        bcba = Bcba(name=name)
        
        result = BcbaService().create(bcba)
        if result.success:
            bcba.id = result.data
            bcbas.append(bcba)
            print(f"  Created BCBA: {bcba.name} (ID: {bcba.id})")
        else:
            print(f"  Failed to create BCBA: {result.error}")
    
    return bcbas

def generate_session_notes(count: int, patients: list, clinics: list, bcbas: list) -> list:
    """Generate fake session notes"""
    print(f"Generating {count} fake session notes...")
    session_notes = []
    
    if not patients:
        print("  No patients available for session notes!")
        return session_notes
    
    if not bcbas:
        print("  No BCBAs available for session notes!")
        return session_notes
    
    for _ in range(count):
        # Random date within last 6 months
        days_ago = random.randint(1, 180)
        session_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Random time during business hours (8 AM - 6 PM)
        hour = random.randint(8, 17)
        minute = random.choice([0, 15, 30, 45])
        session_date = session_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Random session duration (30-120 minutes)
        duration = random.choice([30, 45, 60, 75, 90, 120])
        
        # Select random patient, clinic, and BCBA
        patient = random.choice(patients)
        clinic = random.choice(clinics) if clinics and random.random() > 0.1 else None  # 90% chance of having a clinic
        bcba = random.choice(bcbas)
        
        result = SessionNoteService().create_with_validation(
            bcba=bcba.id,
            patient_id=patient.id,
            notes=generate_note_content(),
            clinic_id=clinic.id if clinic else None,
            apt_date=session_date,
            duration=duration
        )
        
        if result.success:
            session_notes.append(result.data)
            clinic_name = clinic.name if clinic else "No clinic"
            print(f"  Created session note ID {result.data} for {patient.first_name} {patient.last_name} with {bcba.name} at {clinic_name}")
        else:
            print(f"  Failed to create session note: {result.error}")
    
    return session_notes

def main():
    parser = argparse.ArgumentParser(description='Generate fake data for ABA Session Notes application')
    parser.add_argument('--patients', type=int, default=15, help='Number of patients to generate (default: 15)')
    parser.add_argument('--clinics', type=int, default=5, help='Number of clinics to generate (default: 5)')
    parser.add_argument('--bcbas', type=int, default=5, help='Number of BCBAs to generate (default: 5)')
    parser.add_argument('--notes', type=int, default=50, help='Number of session notes to generate (default: 50)')
    
    args = parser.parse_args()
    
    print("🎯 ABA Session Notes - Fake Data Generator")
    print("=" * 50)
    
    try:
        # Generate patients first
        patients = generate_patients(args.patients)
        print(f"✅ Generated {len(patients)} patients\n")
        
        # Generate clinics
        clinics = generate_clinics(args.clinics)
        print(f"✅ Generated {len(clinics)} clinics\n")
        
        # Generate BCBAs
        bcbas = generate_bcbas(args.bcbas)
        print(f"✅ Generated {len(bcbas)} BCBAs\n")
        
        # Generate session notes
        notes = generate_session_notes(args.notes, patients, clinics, bcbas)
        print(f"✅ Generated {len(notes)} session notes\n")
        
        print("🎉 Fake data generation completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Patients: {len(patients)}")
        print(f"   - Clinics: {len(clinics)}")
        print(f"   - BCBAs: {len(bcbas)}")
        print(f"   - Session Notes: {len(notes)}")
        print(f"\n💡 You can now test the application with this generated data.")
        
    except Exception as e:
        print(f"❌ Error generating fake data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 