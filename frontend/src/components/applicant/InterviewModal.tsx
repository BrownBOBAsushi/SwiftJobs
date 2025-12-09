"use client";

import { useState } from "react";

// Define what the backend returns
interface NegotiationResult {
  status: string;
  score: number;
  reason: string;
  log: { sender: string; message: string }[];
}

export default function InterviewModal({ jobId }: { jobId: string }) {
  // State Management
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<NegotiationResult | null>(null);
  const [error, setError] = useState("");

  // --- THE TRIGGER ---
  // We only run this when the user CLICKS the button.
  // This prevents the infinite loop bug.
  const startNegotiation = async () => {
    setIsOpen(true);
    setIsLoading(true);
    setError("");

    try {
      // 1. Prepare the data
      // Note: In a real app, you'd get the resume text from a context or prop
      const payload = {
        job_id: jobId,
        candidate_id: "User (You)", // Sending a string is fine now (since we fixed DB)
        resume_text: "Experienced Python Developer with 3 years of backend experience...",
        job_description: "Looking for a Python Backend Developer...",
        candidate_salary: "$5500",
        hr_budget: "$5000",
      };

      // 2. Call the Backend
      // Make sure this URL matches your backend port (usually 8000)
      const response = await fetch("http://localhost:8000/negotiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
      
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  // --- THE RESET ---
  const handleClose = () => {
    setIsOpen(false);
    setResult(null);
    setIsLoading(false);
    // Optional: Reload page if you want to refresh everything
    // window.location.reload(); 
  };

  return (
    <>
      {/* 1. THE TRIGGER BUTTON */}
      <button
        onClick={startNegotiation}
        disabled={isLoading}
        className="bg-black text-white px-4 py-2 rounded-lg font-bold hover:bg-gray-800 transition shadow-lg flex items-center gap-2"
      >
        {isLoading ? "Negotiating..." : "⚡ Auto-Interview"}
      </button>

      {/* 2. THE MODAL (Only shows if isOpen is true) */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          
          {/* LOADING STATE */}
          {isLoading && (
            <div className="bg-white p-8 rounded-2xl flex flex-col items-center animate-pulse">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-xl font-bold text-gray-800">AI Agents are Fighting...</p>
              <p className="text-gray-500 text-sm">Reviewing Resume vs Job Description</p>
            </div>
          )}

          {/* RESULT STATE (The "Black Box") */}
          {!isLoading && result && (
            <div className="bg-slate-900 text-white p-8 rounded-2xl max-w-md w-full shadow-2xl border border-slate-700 text-center relative">
              
              {/* Score Header */}
              <p className="text-gray-400 text-sm font-mono tracking-widest uppercase mb-2">Match Score</p>
              <h1 className={`text-6xl font-black mb-2 ${result.score > 70 ? 'text-green-400' : 'text-red-400'}`}>
                {result.score}
              </h1>
              
              <div className={`inline-block px-4 py-1 rounded-full text-sm font-bold mb-6 ${
                result.status === 'HIRED' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
              }`}>
                {result.status}
              </div>

              {/* The Reason */}
              <p className="text-gray-300 mb-8 leading-relaxed text-sm">
                "{result.reason}"
              </p>

              {/* --- THE FIX: CLOSE BUTTON --- */}
              <button
                onClick={handleClose}
                className="w-full py-3 bg-white text-black font-bold rounded-xl hover:bg-gray-200 transition transform hover:scale-105"
              >
                Close & Find More Jobs
              </button>
            </div>
          )}

          {/* ERROR STATE */}
          {!isLoading && error && (
            <div className="bg-white p-6 rounded-xl max-w-sm text-center">
              <p className="text-red-600 font-bold mb-4">Error: {error}</p>
              <button onClick={handleClose} className="bg-gray-200 px-4 py-2 rounded-lg">
                Close
              </button>
            </div>
          )}
        </div>
      )}
    </>
  );
}