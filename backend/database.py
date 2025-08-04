from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, String, Date, DateTime, ForeignKey
import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'session_notes.db')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create metadata
metadata = MetaData()

# Define tables
bcbas = Table(
    'bcbas',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', Text, nullable=False)
)

patients = Table(
    'patients',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('first_name', Text, nullable=False),
    Column('last_name', Text, nullable=False),
    Column('DOB', Date, nullable=False),
    Column('ICD', String(15), nullable=True),
    Column('address', Text, nullable=True)
)

clinics = Table(
    'clinics',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', Text, nullable=False),
    Column('address', Text, nullable=True)
)

session_notes = Table(
    'session_notes',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('bcba', Integer, ForeignKey('bcbas.id'), nullable=False),
    Column('patient', Integer, ForeignKey('patients.id'), nullable=False),
    Column('clinic', Integer, ForeignKey('clinics.id'), nullable=True),
    Column('apt_date', DateTime, nullable=False),
    Column('duration', Integer, nullable=True),
    Column('notes', Text, nullable=True)
)

# Create all tables
if __name__ == "__main__":
    metadata.create_all(engine)
    print("Database tables created successfully!") 