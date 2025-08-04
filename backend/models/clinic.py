from pydantic import BaseModel
from typing import Optional

class Clinic(BaseModel):
    """Pydantic model for the clinics table"""
    id: Optional[int] = None
    name: str
    address: Optional[str] = None 