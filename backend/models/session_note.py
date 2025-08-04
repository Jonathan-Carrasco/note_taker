from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionNote(BaseModel):
    id: Optional[int] = None
    bcba: int
    patient: int
    clinic: Optional[int] = None
    apt_date: datetime
    duration: Optional[int] = None
    notes: Optional[str] = None 