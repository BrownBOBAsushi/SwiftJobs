/**
 * Supabase database schema for SwiftJobs application.
 * 
 * This file contains SQL definitions for:
 * - profiles table (users with role: 'applicant' or 'hr')
 * - jobs table (with vector column for embeddings)
 * - matches table (mutual likes between applicants and jobs)
 * - messages table (chat messages between matched users)
 * 
 * Required extensions:
 * - pgvector for vector similarity search
 */

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Profiles table (extends Supabase auth.users)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('applicant', 'hr')),
  full_name TEXT,
  email TEXT,
  avatar_url TEXT,
  company_name TEXT, -- For HR users
  company_logo_url TEXT, -- For HR users
  location TEXT,
  bio TEXT,
  resume_text TEXT, -- For applicants
  resume_embedding vector(1536), -- OpenAI embedding dimension
  preferences JSONB, -- Store preferences as JSON
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  hr_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  company_name TEXT NOT NULL,
  description TEXT NOT NULL,
  requirements TEXT[],
  location TEXT,
  salary_min INTEGER,
  salary_max INTEGER,
  job_type TEXT, -- 'full-time', 'part-time', 'contract', 'internship'
  remote BOOLEAN DEFAULT FALSE,
  description_embedding vector(1536), -- OpenAI embedding for matching
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed', 'draft')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Matches table (mutual likes)
CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  applicant_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  match_score DECIMAL(5, 2), -- 0-100 match score
  applicant_liked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  hr_liked_at TIMESTAMP WITH TIME ZONE,
  matched_at TIMESTAMP WITH TIME ZONE, -- When mutual like occurred
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(applicant_id, job_id)
);

-- Swipes table (track all swipe actions)
CREATE TABLE swipes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  target_id UUID NOT NULL, -- job_id for applicants, applicant_id for HR
  action TEXT NOT NULL CHECK (action IN ('like', 'dislike')),
  user_role TEXT NOT NULL CHECK (user_role IN ('applicant', 'hr')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table (chat between matched users)
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  attachment_url TEXT,
  read_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_profiles_role ON profiles(role);
CREATE INDEX idx_profiles_resume_embedding ON profiles USING ivfflat (resume_embedding vector_cosine_ops);
CREATE INDEX idx_jobs_hr_id ON jobs(hr_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_description_embedding ON jobs USING ivfflat (description_embedding vector_cosine_ops);
CREATE INDEX idx_matches_applicant_id ON matches(applicant_id);
CREATE INDEX idx_matches_job_id ON matches(job_id);
CREATE INDEX idx_matches_matched_at ON matches(matched_at);
CREATE INDEX idx_swipes_user_id ON swipes(user_id);
CREATE INDEX idx_swipes_target_id ON swipes(target_id);
CREATE INDEX idx_messages_match_id ON messages(match_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Row Level Security (RLS) policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE swipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view their own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- RLS Policies for jobs
CREATE POLICY "Anyone can view active jobs"
  ON jobs FOR SELECT
  USING (status = 'active');

CREATE POLICY "HR can create jobs"
  ON jobs FOR INSERT
  WITH CHECK (
    auth.uid() = hr_id AND
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND role = 'hr')
  );

CREATE POLICY "HR can update their own jobs"
  ON jobs FOR UPDATE
  USING (auth.uid() = hr_id);

-- RLS Policies for matches
CREATE POLICY "Users can view their own matches"
  ON matches FOR SELECT
  USING (
    auth.uid() = applicant_id OR
    auth.uid() IN (SELECT hr_id FROM jobs WHERE id = job_id)
  );

-- RLS Policies for swipes
CREATE POLICY "Users can view their own swipes"
  ON swipes FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own swipes"
  ON swipes FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for messages
CREATE POLICY "Users can view messages in their matches"
  ON messages FOR SELECT
  USING (
    auth.uid() = sender_id OR
    auth.uid() IN (
      SELECT applicant_id FROM matches WHERE id = match_id
      UNION
      SELECT hr_id FROM matches m JOIN jobs j ON m.job_id = j.id WHERE m.id = match_id
    )
  );

CREATE POLICY "Users can send messages in their matches"
  ON messages FOR INSERT
  WITH CHECK (
    auth.uid() = sender_id AND
    auth.uid() IN (
      SELECT applicant_id FROM matches WHERE id = match_id
      UNION
      SELECT hr_id FROM matches m JOIN jobs j ON m.job_id = j.id WHERE m.id = match_id
    )
  );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

