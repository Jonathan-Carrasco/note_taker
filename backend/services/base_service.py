from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from utils.result import Result
import traceback

T = TypeVar('T')

class Service(ABC, Generic[T]):
    """
    Abstract base service that enforces consistent patterns across all services
    
    Provides standardized:
    - Error handling
    - Response formatting
    """
      
    @abstractmethod
    def validate(self, data: Any) -> Result:
        """
        Validate the request data specific to this service
        
        Args:
            data: Dict containing the raw request data
            
        Returns:
            Tuple of (is_valid, error_message, processed_data)
            - is_valid: Boolean indicating if validation passed
            - error_message: Error message if validation failed
            - processed_data: Processed data ready for handling
        """
        pass
      
    @abstractmethod
    def execute(self, data: Any) -> Result:
        """
        Main service logic that must be implemented by each service
        
        Args:
            data: Dict containing the request data
            
        Returns:
            Dict with standardized response format
        """
        pass
    
    def process_request(self, data: Any) -> Result:
        """
        Process a request with standardized error handling
        
        This wrapper ensures all service implementations follow the same
        error handling and response format patterns.
        
        Returns:
            Result object with success and data or error
        """
        try:
            # First validate the request data
            result = self.validate(data)
            
            if not result.success:
                return result
            
           # Call the service's implementation with validated data
            return self.execute(result.data)
          
        except Exception as e:
            # Get detailed error information
            error_details = traceback.format_exc()
            error_message = f"Error processing request: {str(e)}"
            
            # Log detailed error for debugging
            print(f"ERROR: {error_message}")
            print(f"DETAILS: {error_details}")
            
            return Result.error_result(error_message, 500) 