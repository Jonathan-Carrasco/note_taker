import openai
from transformers import pipeline
from typing import Optional, Dict, Any
import os

class HuggingFaceLLM:
    def __init__(self, 
                 model_type: str = "openai",
                 model_id: str = "gpt-4o-2024-05-13",
                 api_key: Optional[str] = None,
                 huggingface_model: str = "microsoft/DialoGPT-medium"):
        self.model_type = model_type.lower()
        self.model_id = model_id
        
        # Set up OpenAI client if using OpenAI models
        if self.model_type == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.model_type == "huggingface":
            self.generator = pipeline("text-generation", model=huggingface_model)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def get_note_template(self) -> str:
        """Returns the structured note template for ABA session notes"""
        return """
                **Client Information**
                - Name: [Name], DOB: [MM/DD/YYYY], Insurance: [Name], Diagnosis: [ICD Code]
                - Session Date/Time: [Date], [Start–End], Location: [Home/Clinic/School]
                - Clinician: [Name], Credentials; Units: [X × 15‑min]

                **Goals/Targets**
                - Goal A: description of target, baseline vs. expected performance
                - Goal B: …

                **Interventions Implemented**
                - Intervention A: taught via [DTT/NET/etc.], prompting level [full/partial], reinforcement [type].
                - Intervention B: …

                **Client Response & Observations**
                - For Goal A: ran X trials; client responded correctly Y% of time; error correction applied as needed.
                - For Goal B: …

                **Behavioral Events**
                - Behavior X occurred [when? antecedent]; RBT responded using [strategy]; replacement behaviors observed: [description].

                **Data Summary**
                - Goal-wise performance table or bullet:
                  - Goal A: X trials, Y correct (Y%)…
                  - Behavior incidents: frequency/duration…

                **Plan for Next Session**
                - Suggested adjustments: e.g. increase complexity, fade prompts, change reinforcement.
                - New target programming suggestions: …
              """

    def _call(self, prompt: str, stop: list = None, context: str = "") -> str:
        """Generate text using the specified model with context"""
        try:
            if self.model_type == "openai":
                return self._call_openai(prompt, context)
            elif self.model_type == "huggingface":
                return self._call_huggingface(prompt, context)
        except Exception as e:
            raise Exception(f"Error calling {self.model_type} model: {str(e)}")
    
    def _call_openai(self, prompt: str, context: str = "") -> str:
        """Call OpenAI API with context"""
        system_message = f"""You are an expert ABA (Applied Behavior Analysis) therapist assistant. 
        Generate professional session notes based on the observations provided.
        
        Use this EXACT template structure for the notes and fill in the sections with the provided session data:
        {self.get_note_template()}
        
        Instructions for filling the template:
        - Replace all placeholders in [brackets] with actual session data
        - If specific information is not available, use "Not provided" or "N/A"
        - Maintain the exact formatting and structure of the template
        - Include all sections even if some data is missing
        - Be professional and clinical in tone
        
        Additional context: {context}"""
        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate ABA session notes using the template structure. Fill in the template with this session data: {prompt}"}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def _call_huggingface(self, prompt: str, context: str = "") -> str:
        """Call Hugging Face model with context"""
        full_prompt = f"Context: {context}\n\nObservations: {prompt}\n\nGenerate ABA session notes:"
        result = self.generator(full_prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
        return result[0]["generated_text"][len(full_prompt):].strip()
    
    def generate_note(self, observations: str, context: Dict[str, Any] = None) -> str:
        """
        Generate ABA session notes from observations using the structured template
        
        Args:
            observations: Raw observations from the session
            context: Additional context information (client info, session details, etc.)
        
        Returns:
            Generated ABA session note following the template structure
        """
        context_str = ""
        if context:
            # Build detailed context string for better template population
            context_str = f"""
            Client Name: {context.get('client_name', 'N/A')}
            Date of Birth: {context.get('client_dob', 'N/A')}
            ICD Code/Diagnosis: {context.get('client_icd', 'N/A')}
            Session Date: {context.get('session_date', 'N/A')}
            Session Time: {context.get('session_time', 'N/A')}
            Session Duration: {context.get('session_duration', 'N/A')} minutes
            Location: {context.get('session_location', 'N/A')}
            Clinician: {context.get('clinician', 'N/A')}
            Clinic: {context.get('clinic', 'N/A')}
            Goals/Targets: {context.get('goals', 'N/A')}
            """
        
        return self._call(observations, context=context_str)

