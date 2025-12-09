"use client";
import { useState, useEffect } from "react"; // Import useEffect
import AgentChat from "../components/hr/AgentChat";

const MOCK_CANDIDATES = [
  {
    id: 1,
    name: "Alice Chen (The Perfect Fit)",
    role: "Senior Python Dev",
    salary: "$5500",
    resume: "Expert in FastAPI, Python, and AI Agents. 5 years experience. Built complex backends."
  },
  {
    id: 2,
    name: "Bob Tan (The Lowball)",
    role: "Junior Web Dev",
    salary: "$3000",
    resume: "I know HTML and CSS. I am learning Python. I am very cheap and hardworking."
  },
  {
    id: 3,
    name: "Charlie X (The Mismatch)",
    role: "Java Enterprise Dev",
    salary: "$8000",
    resume: "I hate Python. I only use Java. I expect a very high salary because I am senior."
  }
];

export default function Dashboard() {
  const [jobDescription, setJobDesc] = useState("Looking for a Python Backend Developer. Budget $5000.");
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  
  // --- 1. NEW STATE: To store the real resume text ---
  const [realResumeText, setRealResumeText] = useState("");

  // --- 2. THE CATCH: Check LocalStorage when page loads ---
  useEffect(() => {
    // We check if "window" exists to avoid server-side errors
    if (typeof window !== "undefined") {
      const storedText = localStorage.getItem("my_resume_text");
      if (storedText) {
        console.log("Found real resume!");
        setRealResumeText(storedText);
      }
    }
  }, []);

  // --- 3. THE MERGE: Create a 4th Candidate using your real data ---
  const userCandidate = {
    id: 99,
    name: "User (You - Uploaded Resume)",
    role: "Full Stack Engineer",
    salary: "$5500", // Default target for the demo
    // If text exists, use it. If not, tell them to go upload.
    resume: realResumeText || "No resume uploaded yet. Go to /applicant to upload one." 
  };

  // Add the user to the list
  const allCandidates = [...MOCK_CANDIDATES, userCandidate];

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🚀 Smart Nation Hiring Portal</h1>
        <p className="text-gray-500 mb-8">AI-Powered Autonomous Negotiation System</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* COLUMN 1: THE JOB (HR INPUT) */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-fit">
            <h2 className="font-bold text-lg mb-4">1. Define the Role</h2>
            <label className="text-sm font-bold text-gray-700">Job Description & Budget</label>
            <textarea 
              className="w-full h-40 mt-2 p-3 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              value={jobDescription}
              onChange={(e) => setJobDesc(e.target.value)}
            />
            <p className="text-xs text-gray-400 mt-2">Tip: Try changing the Budget to $2000 to see the AI reject everyone.</p>
          </div>

          {/* COLUMN 2 & 3: THE CANDIDATES */}
          <div className="md:col-span-2 space-y-4">
            <h2 className="font-bold text-lg mb-4">2. Available Candidates (Filtered by AI)</h2>
            
            {/* WE MAP OVER "allCandidates" NOW, NOT "MOCK_CANDIDATES" */}
            {allCandidates.map((c) => (
              <div key={c.id} className={`p-4 rounded-xl shadow-sm border flex justify-between items-center hover:shadow-md transition-all ${c.id === 99 ? "bg-blue-50 border-blue-200" : "bg-white border-gray-200"}`}>
                <div>
                  <h3 className="font-bold text-gray-800">{c.name}</h3>
                  <p className="text-sm text-gray-500">{c.role} • Ask: {c.salary}</p>
                  <p className="text-xs text-gray-400 mt-1 truncate w-96">{c.resume}</p>
                </div>
                
                <button 
                  onClick={() => setSelectedCandidate(c)}
                  className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800"
                >
                  ⚡ Auto-Interview
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* THE MODAL */}
      {selectedCandidate && (
        <AgentChat
          isOpen={!!selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          candidateName={selectedCandidate.name}
          resumeText={selectedCandidate.resume}
          jobDescription={jobDescription}
          budget={jobDescription.match(/\$(\d+)/)?.[0] || "$5000"} 
          targetSalary={selectedCandidate.salary}
        />
      )}
    </div>
  );
}