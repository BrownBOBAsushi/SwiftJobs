"use client";

import ResumeUploader from "../../components/applicant/ResumeUploader";
import InterviewModal from "../../components/applicant/InterviewModal"; // <--- Import the Modal
import Link from "next/link";

export default function ApplicantPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      
      {/* HEADER */}
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
          Smart Nation Career Portal
        </h1>
        <p className="text-gray-500 mt-2 text-lg">
          Upload your resume and let AI fight for your salary.
        </p>
      </div>

      {/* STEP 1: UPLOAD RESUME */}
      <div className="w-full max-w-2xl bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
        <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">
          Step 1: Identity
        </h2>
        <ResumeUploader />
      </div>

      {/* STEP 2: APPLY FOR JOBS (The Demo Section) */}
      <div className="w-full max-w-2xl">
        <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">
          Step 2: Available Positions
        </h2>

        {/* DEMO JOB CARD */}
        <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">Python Backend Developer</h3>
              <p className="text-gray-500 text-sm">TechCorp Systems • Remote</p>
            </div>
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">
              Active Hiring
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-600 mb-6">
            <span className="flex items-center gap-1">
              💰 Budget: <strong>$5,000/mo</strong>
            </span>
            <span className="flex items-center gap-1">
              📅 Exp: <strong>1-3 Years</strong>
            </span>
          </div>

          <div className="flex justify-between items-center border-t pt-4">
            <p className="text-xs text-gray-400">
              *AI Agent will negotiate on your behalf
            </p>
            
            {/* THIS IS THE MAGIC BUTTON */}
            {/* We pass a fake job ID since we fixed the database to accept text */}
            <InterviewModal jobId="job-demo-python-01" />
          </div>
        </div>
      </div>

      {/* FOOTER LINK */}
      <div className="mt-12">
        <Link 
          href="/hr/dashboard" 
          className="text-blue-600 hover:text-blue-800 font-medium hover:underline flex items-center gap-2"
        >
          <span>See Recruiter View</span> 
          <span>→</span>
        </Link>
      </div>
    </div>
  );
}