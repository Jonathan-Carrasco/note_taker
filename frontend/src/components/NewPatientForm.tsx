import { useState } from "react";

interface NewPatientFormProps {
  onSuccess: (patientId: number) => void;
  onCancel: () => void;
}

export default function NewPatientForm({ onSuccess, onCancel }: NewPatientFormProps) {
  const [newPatient, setNewPatient] = useState({
    first_name: "",
    last_name: "",
    DOB: "",
    ICD: "",
    address: ""
  });
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateNewPatient = async () => {
    if (!newPatient.first_name || !newPatient.last_name || !newPatient.DOB) {
      alert("Please fill in all required fields for the new patient (First Name, Last Name, DOB)");
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch("http://localhost:8000/api/patients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          first_name: newPatient.first_name,
          last_name: newPatient.last_name,
          DOB: newPatient.DOB + "T00:00:00Z",  // Convert to UTC datetime
          ICD: newPatient.ICD || null,
          address: newPatient.address || null
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setNewPatient({ first_name: "", last_name: "", DOB: "", ICD: "", address: "" });
        alert("New patient created successfully!");
        onSuccess(result.data);
      } else {
        const error = await response.json();
        alert(`Failed to create patient: ${error.error || error.detail}`);
      }
    } catch (error) {
      alert(`Error creating patient: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-gray-50">
      <h3 className="font-semibold mb-4">Create New Patient</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            First Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={newPatient.first_name}
            onChange={(e) => setNewPatient(prev => ({...prev, first_name: e.target.value}))}
            className="w-full px-3 py-2 border rounded-lg"
            required
            disabled={isCreating}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Last Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={newPatient.last_name}
            onChange={(e) => setNewPatient(prev => ({...prev, last_name: e.target.value}))}
            className="w-full px-3 py-2 border rounded-lg"
            required
            disabled={isCreating}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date of Birth <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            value={newPatient.DOB}
            onChange={(e) => setNewPatient(prev => ({...prev, DOB: e.target.value}))}
            className="w-full px-3 py-2 border rounded-lg"
            required
            disabled={isCreating}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            ICD Code
          </label>
          <input
            type="text"
            value={newPatient.ICD}
            onChange={(e) => setNewPatient(prev => ({...prev, ICD: e.target.value}))}
            className="w-full px-3 py-2 border rounded-lg"
            maxLength={15}
            placeholder="e.g., F84.0"
            disabled={isCreating}
          />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Address
          </label>
          <input
            type="text"
            value={newPatient.address}
            onChange={(e) => setNewPatient(prev => ({...prev, address: e.target.value}))}
            className="w-full px-3 py-2 border rounded-lg"
            placeholder="Patient's address"
            disabled={isCreating}
          />
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        <button
          onClick={handleCreateNewPatient}
          disabled={isCreating}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isCreating ? "Creating..." : "Create Patient"}
        </button>
        <button
          onClick={onCancel}
          disabled={isCreating}
          className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Cancel
        </button>
      </div>
    </div>
  );
} 