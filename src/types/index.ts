/**
 * TypeScript type definitions for the SwiftJobs application.
 * 
 * This file contains all core type definitions including:
 * - User and Profile types
 * - Job types
 * - Match types
 * - Message types
 * - API request/response types
 */

export type UserRole = 'applicant' | 'hr'

export interface User {
  id: string
  email: string
  role: UserRole
  created_at: string
}

export interface Profile {
  id: string
  role: UserRole
  full_name: string | null
  email: string | null
  avatar_url: string | null
  company_name: string | null // For HR users
  company_logo_url: string | null // For HR users
  location: string | null
  bio: string | null
  resume_text: string | null // For applicants
  resume_embedding: number[] | null // For applicants
  preferences: UserPreferences | null
  created_at: string
  updated_at: string
}

export interface UserPreferences {
  desired_roles: string[]
  locations: string[]
  min_salary: number | null
  max_salary: number | null
  job_types: ('full-time' | 'part-time' | 'contract' | 'internship')[] | null
  remote: boolean | null
}

export interface Job {
  id: string
  hr_id: string
  title: string
  company_name: string
  description: string
  requirements: string[]
  location: string | null
  salary_min: number | null
  salary_max: number | null
  job_type: 'full-time' | 'part-time' | 'contract' | 'internship' | null
  remote: boolean
  description_embedding: number[] | null
  status: 'active' | 'closed' | 'draft'
  created_at: string
  updated_at: string
}

export interface Match {
  id: string
  applicant_id: string
  job_id: string
  match_score: number | null
  applicant_liked_at: string
  hr_liked_at: string | null
  matched_at: string | null
  created_at: string
  // Joined data
  job?: Job
  applicant?: Profile
}

export interface Swipe {
  id: string
  user_id: string
  target_id: string
  action: 'like' | 'dislike'
  user_role: UserRole
  created_at: string
}

export interface Message {
  id: string
  match_id: string
  sender_id: string
  content: string
  attachment_url: string | null
  read_at: string | null
  created_at: string
  // Joined data
  sender?: Profile
}

export interface ParsedResume {
  text: string
  structuredData: {
    name: string
    email: string
    phone?: string
    experience: Array<{
      company: string
      title: string
      duration: string
      description: string
    }>
    education: Array<{
      institution: string
      degree: string
      field?: string
      year?: string
    }>
    skills: string[]
  }
  embedding: number[]
}

export interface MatchScoreResult {
  score: number // 0-100
  explanation: string
  matchedSkills: string[]
  missingSkills: string[]
}

// API Request/Response Types
export interface SwipeRequest {
  userId: string
  targetId: string
  action: 'like' | 'dislike'
  userRole: UserRole
}

export interface SwipeResponse {
  success: boolean
  isMatch?: boolean
  matchId?: string
}

export interface MatchScoreRequest {
  applicantId: string
  jobId: string
}

export interface InterviewGenerateRequest {
  jobId: string
  applicantId: string
  focusAreas?: string[]
}

export interface InterviewQuestion {
  id: string
  question: string
  category: string
  expectedAnswer?: string
}

export interface InterviewGenerateResponse {
  questions: InterviewQuestion[]
}

export interface InterviewEvaluateRequest {
  interviewId: string
  questionId: string
  response: string | File
}

export interface InterviewEvaluateResponse {
  score: number
  feedback: string
  strengths: string[]
  improvements: string[]
}

export interface ChatAuthRequest {
  socket_id: string
  channel_name: string
}

export interface ChatAuthResponse {
  auth: string
  channel_data?: string
}

