from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from utils.result import Result
from services.base_service import Service
from hugging_face import HuggingFaceLLM

class NoteGenerationRequest(BaseModel):
    observations: str = Field(..., description="Patient observations from the session")
    model_type: Optional[str] = Field(default="openai", description="Type of model to use (openai or huggingface)")
    model_id: Optional[str] = Field(default="gpt-4o-2024-05-13", description="Specific model ID to use")
    api_key: Optional[str] = Field(default=None, description="API key for the model service")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context information")

class NoteGenerationResponse(BaseModel):
    generated_note: str = Field(..., description="The generated ABA session note")
    model_used: str = Field(..., description="The model that was used to generate the note")
    template_used: bool = Field(default=True, description="Whether the structured template was used")

class NoteTaker(Service[NoteGenerationResponse]):
    """
    Service for generating ABA session notes from patient observations
    """
    
    def validate(self, data: Any) -> Result:
        """
        Validate the note generation request data using Pydantic
        
        Args:
            data: Raw request data
            
        Returns:
            Result containing validated NoteGenerationRequest or error
        """
        try:
            # Let Pydantic handle all validation
            validated_request = NoteGenerationRequest(**data)
            return Result.success_result(validated_request)
            
        except ValidationError as e:
            return Result.error_result(f"Validation error: {str(e)}", 400)
        except Exception as e:
            return Result.error_result(f"Unexpected validation error: {str(e)}", 500)
    
    def execute(self, validated_data: NoteGenerationRequest) -> Result:
        """
        Execute note generation using the specified LLM
        
        Args:
            validated_data: Validated NoteGenerationRequest
            
        Returns:
            Result containing NoteGenerationResponse or error
        """
        try:
            # Initialize the LLM with the specified parameters
            llm = HuggingFaceLLM(
                model_type=validated_data.model_type,
                model_id=validated_data.model_id,
                api_key=validated_data.api_key
            )
            
            # Generate the note
            generated_note = llm.generate_note(
                observations=validated_data.observations,
                context=validated_data.context
            )
            
            # Create response object
            response = NoteGenerationResponse(
                generated_note=generated_note,
                model_used=f"{validated_data.model_type}:{validated_data.model_id}",
                template_used=True
            )
            
            return Result.success_result(response)
            
        except Exception as e:
            return Result.error_result(f"Note generation failed: {str(e)}", 500)
    
    def generate_simple_note(self, observations: str, model_type: str = "openai") -> Result:
        """
        Convenience method for simple note generation
        
        Args:
            observations: Patient observations
            model_type: Model type to use (default: openai)
            
        Returns:
            Result containing generated note or error
        """
        data = {
            "observations": observations,
            "model_type": model_type
        }
        
        return self.process_request(data) 