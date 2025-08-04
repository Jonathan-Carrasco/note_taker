"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import SessionDetailsForm from "../../components/SessionDetailsForm";
import NoteGenerationForm from "../../components/NoteGenerationForm";

export default function GenerateNote() {
  // Form fields using only numbers (-1 = new patient, 0 = no selection)
  const [selectedPatient, setSelectedPatient] = useState<number>(0);
  const [selectedClinic, setSelectedClinic] = useState<number>(0);
  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("");
  const [duration, setDuration] = useState<number>(0);

  // Set default date and time (local time for user input)
  useEffect(() => {
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const currentTime = now.toTimeString().slice(0, 5);
    
    setAppointmentDate(today);
    setAppointmentTime(currentTime);
  }, []);



  const handleNoteGenerated = (note: string) => {
    console.log("Note generated:", note.substring(0, 100) + "...");
  };

  const handleNoteSaved = () => {
    console.log("Note saved successfully");
  };

  return (
    <div className="flex min-h-screen flex-col p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Generate Note</h1>
        <div className="flex gap-4">
          <Link href="/saved-notes" className="text-blue-600 hover:underline">
            View Saved Notes
          </Link>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Home
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Session Details */}
        <SessionDetailsForm
          selectedPatient={selectedPatient}
          selectedClinic={selectedClinic}
          appointmentDate={appointmentDate}
          appointmentTime={appointmentTime}
          duration={duration}
          onPatientChange={setSelectedPatient}
          onClinicChange={setSelectedClinic}
          onDateChange={setAppointmentDate}
          onTimeChange={setAppointmentTime}
          onDurationChange={setDuration}
        />

        {/* Right Column - Note Generation */}
        <NoteGenerationForm
          selectedPatient={selectedPatient}
          selectedClinic={selectedClinic}
          appointmentDate={appointmentDate}
          appointmentTime={appointmentTime}
          duration={duration}
          onNoteGenerated={handleNoteGenerated}
          onNoteSaved={handleNoteSaved}
        />
      </div>
    </div>
  );
}
