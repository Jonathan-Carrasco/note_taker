from pydantic import BaseModel
from datetime import date
from typing import Optional

class Patient(BaseModel):
    """Pydantic model for the patients table"""
    id: Optional[int] = None
    first_name: str
    last_name: str
    DOB: date
    ICD: Optional[str] = None
    address: Optional[str] = None 