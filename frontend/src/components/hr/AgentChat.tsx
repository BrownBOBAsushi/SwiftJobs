// frontend/src/components/hr/AgentChat.tsx

"use client";
import { useState, useEffect } from "react";

// 1. Define what data this component NEEDS to work
interface AgentChatProps {
  isOpen: boolean;
  onClose: () => void;
  candidateName: string;
  resumeText: string;    // <--- Dynamic Input
  jobDescription: string; // <--- Dynamic Input
  budget: string;         // <--- Dynamic Input
  targetSalary: string;   // <--- Dynamic Input
}

export default function AgentChat({ 
  isOpen, onClose, candidateName, resumeText, jobDescription, budget, targetSalary 
}: AgentChatProps) {
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // 2. Auto-start the battle when the modal opens
  useEffect(() => {
    if (isOpen && !result && !loading) {
      startNegotiation();
    }
  }, [isOpen]);

  const startNegotiation = async () => {
    setLoading(true);
    try {
      // 3. Use the REAL data passed via props
      const payload = {
        candidate_id: candidateName, 
        job_id: "job-123",
        resume_text: resumeText,
        job_description: jobDescription,
        candidate_salary: targetSalary,
        hr_budget: budget
      };

      const res = await fetch("http://127.0.0.1:8000/negotiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    // Simple Modal Overlay
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white w-full max-w-2xl rounded-xl shadow-2xl overflow-hidden relative">
        
        {/* Header */}
        <div className="bg-gray-900 p-4 flex justify-between items-center text-white">
          <h2 className="font-bold">⚡ Interviewing: {candidateName}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">✕</button>
        </div>

        {/* Chat Area */}
        <div className="h-[400px] overflow-y-auto p-4 bg-gray-50 space-y-4">
          {loading && (
            <div className="text-center mt-20">
              <div className="animate-spin h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"/>
              <p className="text-gray-500 mt-4 animate-pulse">Agents are negotiating...</p>
            </div>
          )}

          {result?.log.map((msg: any, idx: number) => (
             <div key={idx} className={`flex ${msg.sender === "HR" ? "justify-end" : "justify-start"}`}>
               <div className={`max-w-[80%] p-3 rounded-2xl text-sm shadow-sm ${
                 msg.sender === "HR" ? "bg-blue-600 text-white" : "bg-white text-gray-800 border"
               }`}>
                 <div className="text-xs font-bold opacity-70 mb-1">{msg.sender} Agent</div>
                 {msg.message}
               </div>
             </div>
          ))}
        </div>

        {/* Inside AgentChat.tsx return() */}
        {result && (
            <div className="mt-4 space-y-3">
                {/* THE SCORE CARD */}
                <div className="bg-gray-900 text-white p-6 rounded-xl text-center">
                    <div className="text-sm uppercase tracking-widest opacity-70">Match Score</div>
                    <div className={`text-6xl font-black my-2 ${
                        result.score > 95 ? "text-green-400" : 
                        result.score > 70 ? "text-blue-400" : "text-red-400"
                    }`}>
                        {result.score}
                    </div>
                    <div className="text-xl font-bold">{result.status}</div>
                    <p className="text-gray-400 text-sm mt-2 px-4 italic">"{result.reason}"</p>
                </div>
            </div>
        )}

        {/* THE SCORE CARD */}
        {result && (
            <div className="mt-4 p-6 bg-white border-t border-gray-100 rounded-b-xl">
                <div className="flex items-center justify-between mb-2">
                <div>
                    <div className="text-xs font-bold text-gray-400 uppercase tracking-widest">Match Score</div>
                    <div className={`text-5xl font-black ${
                    result.score > 80 ? "text-green-500" : result.score > 50 ? "text-yellow-500" : "text-red-500"
                    }`}>
                    {result.score}
                    </div>
                </div>
                <div className={`px-4 py-2 rounded-lg font-bold text-xl ${
                    result.status === "HIRED" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                }`}>
                    {result.status}
                </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                <span className="text-xs font-bold text-gray-500">JUDGE'S REASONING:</span>
                <p className="text-sm text-gray-700 italic mt-1">"{result.reason}"</p>
                </div>
            </div>
        )}
      </div>
    </div>
  );
}