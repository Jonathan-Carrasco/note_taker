
from typing import Any, Dict, TypeVar
from pydantic import BaseModel
from enum import StrEnum

T = TypeVar('T', bound=BaseModel)

class Payload(StrEnum):
  payload = "data"
  success = "success"
  error = "error"
  status_code = "status_code"

class Result:
    """
    Standardized result class for service responses
    
    Attributes:
        success: Boolean indicating if the operation was successful
        data: Response data (when success is True)
        error: Error message (when success is False)
        status_code: HTTP status code
    """
    
    def __init__(
        self, 
        success: bool,
        data: Any = None,
        error: str = None,
        status_code: int = None
    ):
        self.success = success
        self.data = data if success else None
        self.error = error if not success else None
        self.status_code = status_code or (200 if success else 500)
    
    @classmethod
    def success_result(cls, data: Any = None) -> 'Result':
        """Create a successful result with the given data"""
        return cls(success=True, data=data)
    
    @classmethod
    def error_result(cls, error: str, status_code: int = 400) -> 'Result':
        """Create an error result with the given error message"""
        return cls(success=False, error=error, status_code=status_code)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary representation"""
        result = {Payload.success: self.success, Payload.status_code: self.status_code}
        if self.success:
            result[Payload.payload] = self.data
        else:
            result[Payload.error] = self.error
        return result

    def to_response(self):
        """Convert result to an HTTP response"""
        if self.success:
            if isinstance(self.data, list):
                print(f"RESPONSE DATA: type: {type(self.data)}, data: {', '.join(str(item) for item in self.data)}")
            else:
                print(f"RESPONSE DATA: type: {type(self.data)}, data: {str(self.data)}")
            return {Payload.payload: self.data}
        else:
            print(f"RESPONSE ERROR: {str(self.error)}")
            return {Payload.error: self.error}
