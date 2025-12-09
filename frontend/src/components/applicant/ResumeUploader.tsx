"use client";
import { useState } from "react";

export default function ResumeUploader() {
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");
  const [status, setStatus] = useState<"IDLE" | "SUCCESS" | "ERROR">("IDLE");

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setFileName(file.name);
    setStatus("IDLE");

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Send PDF to Python Backend
      // NOTE: Ensure your Python server is running on port 8000!
      const res = await fetch("http://127.0.0.1:8000/parse-resume", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to parse PDF");

      const data = await res.json();
      console.log("✅ Extracted Text:", data.text);

      // 2. Save text to LocalStorage (The "Memory" for the demo)
      // The Dashboard will read this later to create the "You" candidate.
      localStorage.setItem("my_resume_text", data.text);
      localStorage.setItem("my_resume_name", file.name);

      setStatus("SUCCESS");
    } catch (error) {
      console.error(error);
      setStatus("ERROR");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <h2 className="text-xl font-bold mb-4 text-gray-800">📄 Upload Your Resume</h2>
      
      <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:bg-gray-50 transition-colors">
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange}
          disabled={loading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        {loading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mb-2"></div>
            <p className="text-sm text-gray-500">Reading PDF...</p>
          </div>
        ) : (
          <div>
            <div className="text-4xl mb-2">📂</div>
            <p className="font-medium text-gray-700">Click to upload PDF</p>
            <p className="text-xs text-gray-400 mt-1">AI Agent will extract skills automatically</p>
          </div>
        )}
      </div>

      {/* STATUS INDICATORS */}
      {status === "SUCCESS" && (
        <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm flex items-center">
          ✅ <b>Success!</b>&nbsp; Resume "{fileName}" processed. Go to Dashboard.
        </div>
      )}
      
      {status === "ERROR" && (
        <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          ❌ <b>Error.</b> Is your Python Backend running?
        </div>
      )}
    </div>
  );
}