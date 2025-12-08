/**
 * Validation utilities for form inputs and data.
 * 
 * Responsibilities:
 * - Email validation
 * - Password strength validation
 * - File type and size validation
 * - Form field validation schemas
 * 
 * Required imports:
 * - zod (for schema validation)
 * - Custom validation functions
 */

import { z } from 'zod'

export const emailSchema = z.string().email()
export const passwordSchema = z.string().min(8)
export const fileSchema = z.instanceof(File)

// Add more validation schemas as needed

