"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface SessionNote {
  id: number;
  bcba: number;
  patient: number;
  clinic: number;
  apt_date: string;
  duration: number;
  notes: string;
  patient_name: string;
  clinic_name: string;
}

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

export default function SavedNotes() {
  const [notes, setNotes] = useState<SessionNote[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [bcbaId, setBcbaId] = useState(123);
  const [selectedNote, setSelectedNote] = useState<SessionNote | null>(null);
  const [editingNote, setEditingNote] = useState<SessionNote | null>(null);
  const [editForm, setEditForm] = useState({
    notes: "",
    patient_id: 0,
    clinic_id: 0,
    apt_date: "",
    apt_time: "",
    duration: 0
  });

  // Convert UTC time to local for display
  const convertFromUTC = (utcDateTime: string): { date: string; time: string } => {
    const date = new Date(utcDateTime);
    const localDate = date.getFullYear() + '-' + 
      String(date.getMonth() + 1).padStart(2, '0') + '-' + 
      String(date.getDate()).padStart(2, '0');
    const localTime = String(date.getHours()).padStart(2, '0') + ':' + 
      String(date.getMinutes()).padStart(2, '0');
    return { date: localDate, time: localTime };
  };

  // Convert local time to UTC for storage
  const convertToUTC = (date: string, time: string): string => {
    const localDateTime = new Date(`${date}T${time}`);
    return localDateTime.toISOString();
  };

  const fetchNotes = async (bcbaId: number) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/session-notes?bcba_id=${bcbaId}`);
      
      if (response.ok) {
        const result = await response.json();
        if (result.data && Array.isArray(result.data)) {
          setNotes(result.data);
        } else {
          setNotes([]);
        }
      } else {
        const error = await response.json();
        setError(`Failed to fetch notes: ${error.error || error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      setError(`Error fetching notes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchPatientsAndClinics = async () => {
    try {
      const [patientsRes, clinicsRes] = await Promise.all([
        fetch("http://localhost:8000/api/patients").then(res => res.json()),
        fetch("http://localhost:8000/api/clinics").then(res => res.json())
      ]);
      
      if (patientsRes.data) setPatients(patientsRes.data);
      if (clinicsRes.data) setClinics(clinicsRes.data);
    } catch (error) {
      console.error("Error loading patients/clinics:", error);
    }
  };

  useEffect(() => {
    fetchNotes(bcbaId);
    fetchPatientsAndClinics();
  }, [bcbaId]);

  const handleViewNote = (note: SessionNote) => {
    setSelectedNote(note);
  };

  const handleEditNote = (note: SessionNote) => {
    setEditingNote(note);
    
    // Parse UTC datetime to local for editing
    const { date, time } = convertFromUTC(note.apt_date);
    
    setEditForm({
      notes: note.notes || "",
      patient_id: note.patient,
      clinic_id: note.clinic || 0,
      apt_date: date,
      apt_time: time,
      duration: note.duration || 0
    });
  };

  const handleSaveEdit = async () => {
    if (!editingNote) return;

    try {
      const appointmentDateTime = convertToUTC(editForm.apt_date, editForm.apt_time);
      
      const response = await fetch(`http://localhost:8000/api/session-notes/${editingNote.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          notes: editForm.notes,
          patient_id: editForm.patient_id,
          clinic_id: editForm.clinic_id || null,
          apt_date: appointmentDateTime,
          duration: editForm.duration || null
        }),
      });

      if (response.ok) {
        alert("Note updated successfully!");
        setEditingNote(null);
        fetchNotes(bcbaId); // Refresh the list
      } else {
        const error = await response.json();
        alert(`Failed to update note: ${error.error || error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Error updating note: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm("Are you sure you want to delete this note? This action cannot be undone.")) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/session-notes/${noteId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        alert("Note deleted successfully!");
        fetchNotes(bcbaId); // Refresh the list
        if (selectedNote && selectedNote.id === noteId) {
          setSelectedNote(null);
        }
      } else {
        const error = await response.json();
        alert(`Failed to delete note: ${error.error || error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Error deleting note: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const closeModal = () => {
    setSelectedNote(null);
  };

  const closeEditModal = () => {
    setEditingNote(null);
  };

  const formatDateTime = (dateTimeString: string) => {
    const { date, time } = convertFromUTC(dateTimeString);
    return {
      date: new Date(date).toLocaleDateString(),
      time: time
    };
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <div className="flex min-h-screen flex-col p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Saved Notes</h1>
        <div className="flex gap-4">
          <Link href="/generate" className="text-blue-600 hover:underline">
            Generate New Note
          </Link>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Home
          </Link>
        </div>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          BCBA ID:
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            value={bcbaId}
            onChange={(e) => setBcbaId(parseInt(e.target.value) || 123)}
            className="px-3 py-2 border rounded-lg w-24"
            min="1"
          />
          <button
            onClick={() => fetchNotes(bcbaId)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-8">
          <p>Loading notes...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!loading && !error && notes.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No notes found for BCBA ID {bcbaId}.</p>
          <p className="mt-2">
            <Link href="/generate" className="text-blue-600 hover:underline">
              Generate your first note
            </Link>
          </p>
        </div>
      )}

      {!loading && !error && notes.length > 0 && (
        <div className="space-y-4">
          <p className="text-gray-600 mb-4">
            Found {notes.length} note{notes.length !== 1 ? 's' : ''} for BCBA ID {bcbaId}
          </p>
          
          {notes.map((note) => {
            const { date, time } = formatDateTime(note.apt_date);
            return (
              <div key={note.id} className="p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <span><strong>Date:</strong> {date}</span>
                      <span><strong>Time:</strong> {time}</span>
                      <span><strong>Duration:</strong> {note.duration ? `${note.duration} min` : 'N/A'}</span>
                      <span><strong>Note ID:</strong> {note.id}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mb-3">
                      <span><strong>Patient:</strong> {note.patient_name}</span>
                      <span><strong>Clinic:</strong> {note.clinic_name}</span>
                    </div>
                    <p className="text-gray-800">
                      {note.notes ? truncateText(note.notes) : "No notes content"}
                    </p>
                  </div>
                  <div className="ml-4 flex flex-col gap-2">
                    <button
                      onClick={() => handleViewNote(note)}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleEditNote(note)}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteNote(note.id)}
                      className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* View Modal */}
      {selectedNote && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Session Note Details</h2>
                <button
                  onClick={closeModal}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div><strong>Note ID:</strong> {selectedNote.id}</div>
                <div><strong>BCBA ID:</strong> {selectedNote.bcba}</div>
                <div><strong>Patient:</strong> {selectedNote.patient_name}</div>
                <div><strong>Clinic:</strong> {selectedNote.clinic_name}</div>
                <div><strong>Date:</strong> {formatDateTime(selectedNote.apt_date).date}</div>
                <div><strong>Time:</strong> {formatDateTime(selectedNote.apt_date).time}</div>
                <div><strong>Duration:</strong> {selectedNote.duration ? `${selectedNote.duration} minutes` : 'Not specified'}</div>
              </div>
              
              <div className="mt-4">
                <strong className="block mb-2">Notes:</strong>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="whitespace-pre-wrap text-sm">
                    {selectedNote.notes || "No notes content"}
                  </pre>
                </div>
              </div>
            </div>
            
            <div className="p-6 border-t">
              <button
                onClick={closeModal}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingNote && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Edit Session Note</h2>
                <button
                  onClick={closeEditModal}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <div className="space-y-4">
                {/* Patient Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Patient
                  </label>
                  <select
                    value={editForm.patient_id}
                    onChange={(e) => setEditForm(prev => ({...prev, patient_id: parseInt(e.target.value)}))}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    {patients.map(patient => (
                      <option key={patient.id} value={patient.id}>
                        {patient.first_name} {patient.last_name} (DOB: {patient.DOB})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Clinic Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Clinic
                  </label>
                  <select
                    value={editForm.clinic_id}
                    onChange={(e) => setEditForm(prev => ({...prev, clinic_id: parseInt(e.target.value) || 0}))}
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
                      Appointment Date
                    </label>
                    <input
                      type="date"
                      value={editForm.apt_date}
                      onChange={(e) => setEditForm(prev => ({...prev, apt_date: e.target.value}))}
                      className="w-full px-3 py-2 border rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Appointment Time
                    </label>
                    <input
                      type="time"
                      value={editForm.apt_time}
                      onChange={(e) => setEditForm(prev => ({...prev, apt_time: e.target.value}))}
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
                    value={editForm.duration || ""}
                    onChange={(e) => setEditForm(prev => ({...prev, duration: parseInt(e.target.value) || 0}))}
                    className="w-full px-3 py-2 border rounded-lg"
                    min="1"
                    max="240"
                    placeholder="e.g., 60"
                  />
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Session Notes
                  </label>
                  <textarea
                    value={editForm.notes}
                    onChange={(e) => setEditForm(prev => ({...prev, notes: e.target.value}))}
                    className="w-full h-48 p-4 border rounded-lg"
                    placeholder="Enter session notes..."
                  />
                </div>
              </div>
            </div>
            
            <div className="p-6 border-t flex gap-2">
              <button
                onClick={handleSaveEdit}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                Save Changes
              </button>
              <button
                onClick={closeEditModal}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
