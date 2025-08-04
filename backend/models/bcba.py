from pydantic import BaseModel
from typing import Optional

class Bcba(BaseModel):
    """Pydantic model for the bcbas table"""
    id: Optional[int] = None
    name: str 