import { useState, useEffect } from "react";
import NewPatientForm from "./NewPatientForm";

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

interface SessionDetailsFormProps {
  selectedPatient: number;
  selectedClinic: number;
  appointmentDate: string;
  appointmentTime: string;
  duration: number;
  onPatientChange: (patientId: number) => void;
  onClinicChange: (clinicId: number) => void;
  onDateChange: (date: string) => void;
  onTimeChange: (time: string) => void;
  onDurationChange: (duration: number) => void;
}

export default function SessionDetailsForm({
  selectedPatient,
  selectedClinic,
  appointmentDate,
  appointmentTime,
  duration,
  onPatientChange,
  onClinicChange,
  onDateChange,
  onTimeChange,
  onDurationChange
}: SessionDetailsFormProps) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewPatientForm, setShowNewPatientForm] = useState(false);

  // Load patients and clinics
  useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/patients").then(res => res.json()),
      fetch("http://localhost:8000/api/clinics").then(res => res.json())
    ]).then(([patientsRes, clinicsRes]) => {
      if (patientsRes.data) setPatients(patientsRes.data);
      if (clinicsRes.data) setClinics(clinicsRes.data);
      setLoading(false);
    }).catch(error => {
      console.error("Error loading data:", error);
      setLoading(false);
    });
  }, []);

  const handlePatientSelectChange = (value: string) => {
    const numValue = parseInt(value);
    if (numValue === -1) {
      setShowNewPatientForm(true);
      onPatientChange(-1);
    } else {
      setShowNewPatientForm(false);
      onPatientChange(numValue || 0);
    }
  };

  const handleNewPatientSuccess = async (patientId: number) => {
    // Refresh patients list
    try {
      const patientsRes = await fetch("http://localhost:8000/api/patients").then(res => res.json());
      if (patientsRes.data) setPatients(patientsRes.data);
      
      // Select the new patient
      onPatientChange(patientId);
      setShowNewPatientForm(false);
    } catch (error) {
      console.error("Error refreshing patients:", error);
    }
  };

  const handleNewPatientCancel = () => {
    setShowNewPatientForm(false);
    onPatientChange(0);
  };



  if (loading) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Session Details</h2>
        <p>Loading patients and clinics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Session Details</h2>
      
      {/* Patient Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Patient <span className="text-red-500">*</span>
        </label>
        <select
          value={selectedPatient}
          onChange={(e) => handlePatientSelectChange(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
          required
        >
          <option value={0}>Select a patient...</option>
          {patients.map(patient => (
            <option key={patient.id} value={patient.id}>
              {patient.first_name} {patient.last_name} (DOB: {patient.DOB})
            </option>
          ))}
          <option value={-1}>➕ Create New Patient</option>
        </select>
      </div>

      {/* New Patient Form */}
      {showNewPatientForm && (
        <NewPatientForm
          onSuccess={handleNewPatientSuccess}
          onCancel={handleNewPatientCancel}
        />
      )}

      {/* Clinic Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Clinic
        </label>
        <select
          value={selectedClinic}
          onChange={(e) => onClinicChange(parseInt(e.target.value) || 0)}
          className="w-full px-3 py-2 border rounded-lg"
        >
          <option value={0}>Select a clinic (optional)...</option>
          {clinics.map(clinic => (
            <option key={clinic.id} value={clinic.id}>
              {clinic.name}
            </option>
          ))}
        </select>
      </div>

      {/* Date and Time */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Appointment Date <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={appointmentDate}
            onChange={(e) => onDateChange(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Appointment Time <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            value={appointmentTime}
            onChange={(e) => onTimeChange(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg"
            required
          />
        </div>
      </div>

      {/* Duration */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Duration (minutes)
        </label>
        <input
          type="number"
          value={duration || ""}
          onChange={(e) => onDurationChange(parseInt(e.target.value) || 0)}
          className="w-full px-3 py-2 border rounded-lg"
          min="1"
          max="240"
          placeholder="e.g., 60"
        />
      </div>
    </div>
  );
} 