# SwiftJobs - Tinder for Jobs

AI-powered job matching platform built with Next.js 14, Supabase, and OpenAI.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/UI
- **Database**: Supabase (PostgreSQL with pgvector)
- **AI**: OpenAI (for resume parsing and match scoring)
- **Real-time**: Pusher (for chat)
- **Animations**: Framer Motion

## Project Structure

```
src/
├── app/              # Next.js App Router pages
├── components/       # React components
├── lib/             # Utilities and integrations
├── types/           # TypeScript type definitions
└── config/          # Configuration constants
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Initialize Supabase:
   - Run the SQL schema from `src/lib/supabase/schema.sql`
   - Configure environment variables for Supabase

4. Install Shadcn UI components:
```bash
npx shadcn-ui@latest init
```

5. Run the development server:
```bash
npm run dev
```

## Features

- **Swipe to Apply**: Tinder-like interface for job matching
- **AI Resume Parsing**: Automatic resume extraction and structuring
- **Smart Matching**: Vector similarity-based job matching
- **Real-time Chat**: Messaging between applicants and HR
- **Mock Interviews**: AI-powered interview preparation

## License

MIT
