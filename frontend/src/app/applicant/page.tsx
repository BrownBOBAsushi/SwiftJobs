import ResumeUploader from "../../components/applicant/ResumeUploader";
import Link from "next/link";

export default function ApplicantPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Smart Nation Career Portal</h1>
        <p className="text-gray-500">Let our AI Agent negotiate your salary for you.</p>
      </div>

      <ResumeUploader />

      <div className="mt-8">
        <Link 
          href="/" 
          className="text-blue-600 hover:text-blue-800 font-medium hover:underline"
        >
          → Go to Recruiter Dashboard (See the magic)
        </Link>
      </div>
    </div>
  );
}