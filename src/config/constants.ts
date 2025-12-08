/**
 * Application constants and configuration values.
 * 
 * Responsibilities:
 * - Define application-wide constants
 * - Configuration values
 * - Default values
 * - Feature flags
 */

export const APP_NAME = 'SwiftJobs'
export const APP_DESCRIPTION = 'AI-powered job matching platform'

// API endpoints
export const API_ROUTES = {
  RESUME_PARSE: '/api/resume/parse',
  MATCH_SCORE: '/api/match/score',
  SWIPE: '/api/swipe',
  CHAT_AUTH: '/api/chat',
  INTERVIEW_GENERATE: '/api/interview/generate',
  INTERVIEW_EVALUATE: '/api/interview/evaluate',
} as const

// File upload constraints
export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
export const ALLOWED_RESUME_TYPES = ['application/pdf']

// Match score thresholds
export const MIN_MATCH_SCORE = 0
export const MAX_MATCH_SCORE = 100
export const DEFAULT_MIN_MATCH_SCORE = 70

// Pagination
export const DEFAULT_PAGE_SIZE = 20

// Pusher configuration
export const PUSHER_CHANNEL_PREFIX = 'private-match-'

// OpenAI configuration
export const OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'
export const OPENAI_EMBEDDING_DIMENSION = 1536

