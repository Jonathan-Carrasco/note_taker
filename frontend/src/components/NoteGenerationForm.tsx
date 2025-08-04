import { useState, useEffect } from "react";

interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  DOB: string;
  ICD?: string;
  address?: string;
}

interface Clinic {
  id: number;
  name: string;
  address?: string;
}

interface NoteGenerationFormProps {
  selectedPatient: number;
  selectedClinic: number;
  appointmentDate: string;
  appointmentTime: string;
  duration: number;
  onNoteGenerated?: (note: string) => void;
  onNoteSaved?: () => void;
}

export default function NoteGenerationForm({
  selectedPatient,
  selectedClinic,
  appointmentDate,
  appointmentTime,
  duration,
  onNoteGenerated,
  onNoteSaved
}: NoteGenerationFormProps) {
  const [observations, setObservations] = useState("");
  const [generatedNote, setGeneratedNote] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [clinics, setClinics] = useState<Clinic[]>([]);

  // Load patients and clinics data for context
  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/patients").then(res => res.json()),
      fetch("http://localhost:8000/api/clinics").then(res => res.json())
    ]).then(([patientsRes, clinicsRes]) => {
      if (patientsRes.data) setPatients(patientsRes.data);
      if (clinicsRes.data) setClinics(clinicsRes.data);
    }).catch(error => {
      console.error("Error loading data:", error);
    });
  }, []);

  // Convert local time to UTC for storage
  const convertToUTC = (date: string, time: string): string => {
    const localDateTime = new Date(`${date}T${time}`);
    return localDateTime.toISOString();
  };

  // Build context object for LLM
  const buildContext = () => {
    const selectedPatientData = patients.find(p => p.id === selectedPatient);
    const selectedClinicData = clinics.find(c => c.id === selectedClinic);
    
    const sessionDateTime = convertToUTC(appointmentDate, appointmentTime);
    const sessionDate = new Date(sessionDateTime);
    
    return {
      client_name: selectedPatientData 
        ? `${selectedPatientData.first_name} ${selectedPatientData.last_name}` 
        : "N/A",
      client_dob: selectedPatientData?.DOB || "N/A",
      client_icd: selectedPatientData?.ICD || "N/A",
      session_date: sessionDate.toLocaleDateString(),
      session_time: `${appointmentTime} - ${appointmentTime}`, // You may want to calculate end time
      session_duration: duration || "N/A",
      session_location: selectedClinicData?.name || "N/A",
      clinician: "N/A", // This could be made configurable
      clinic: selectedClinicData?.name || "N/A",
      goals: "To be determined based on observations" // This could be enhanced
    };
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const context = buildContext();
      
      const response = await fetch("http://localhost:8000/api/llm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",  
        },
        body: JSON.stringify({ 
          observations: observations,
          model_type: "openai",
          model_id: "gpt-4o-2024-05-13",
          context: context
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data && result.data.generated_note) {
          setGeneratedNote(result.data.generated_note);
          onNoteGenerated?.(result.data.generated_note);
        } else {
          setGeneratedNote("Failed to generate note - no data received");
        }
      } else {
        const error = await response.json();
        setGeneratedNote(`Failed to generate note: ${error.error || error.detail}`);
      }
    } catch (error) {
      setGeneratedNote(`Error generating note: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!generatedNote) {
      alert("No note to save. Please generate a note first.");
      return;
    }

    if (!selectedPatient || selectedPatient === -1) {
      alert("Please select a patient.");
      return;
    }

    if (!appointmentDate || !appointmentTime) {
      alert("Please select appointment date and time.");
      return;
    }

    setIsSaving(true);
    try {
      const appointmentDateTime = convertToUTC(appointmentDate, appointmentTime);

      const response = await fetch("http://localhost:8000/api/session-notes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          bcba: 123, // Default BCBA ID - could be made configurable
          patient_id: selectedPatient,
          clinic_id: selectedClinic || null,
          apt_date: appointmentDateTime,
          duration: duration || null,
          notes: generatedNote
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.data) {
          alert(`Note saved successfully! Note ID: ${result.data}`);
          // Reset form
          setGeneratedNote("");
          setObservations("");
          onNoteSaved?.();
        } else {
          alert("Note saved successfully!");
        }
      } else {
        const error = await response.json();
        alert(`Failed to save note: ${error.error || error.detail || JSON.stringify(error)}`);
      }
    } catch (error) {
      alert(`Error saving note: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Note Generation</h2>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Patient Observations <span className="text-red-500">*</span>
        </label>
        <textarea
          className="w-full h-48 p-4 border rounded-lg"
          placeholder="Enter your observations here..."
          value={observations}
          onChange={(e) => setObservations(e.target.value)}
          required
          disabled={isGenerating}
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={!observations.trim() || isGenerating}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isGenerating ? "Generating..." : "Generate Note"}
      </button>

      {generatedNote && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Generated Note</h3>
          <div className="p-4 border rounded-lg bg-gray-50 max-h-96 overflow-y-auto">
            <pre className="whitespace-pre-wrap text-sm">{generatedNote}</pre>
          </div>
          <button
            onClick={handleSave}
            disabled={!selectedPatient || selectedPatient === -1 || selectedPatient === 0 || !appointmentDate || !appointmentTime || isSaving}
            className="w-full mt-4 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isSaving ? "Saving..." : "Save Note"}
          </button>
          {(!selectedPatient || selectedPatient === -1 || selectedPatient === 0 || !appointmentDate || !appointmentTime) && (
            <p className="text-sm text-red-600 mt-2">
              Please fill in all required fields (Patient, Date, Time) before saving.
            </p>
          )}
        </div>
      )}
    </div>
  );
} 