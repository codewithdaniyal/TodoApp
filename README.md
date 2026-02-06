# Todo Full-Stack Web Application

A secure, multi-user Todo application built with Next.js 16+, FastAPI, and Neon PostgreSQL using spec-driven development methodology.

## Features

- **User Authentication**: Secure signup/signin with Better Auth JWT tokens
- **Task Management**: Full CRUD operations (Create, Read, Update, Delete, Complete)
- **Multi-User Support**: Strict user isolation - users only see their own tasks
- **Persistent Storage**: Neon Serverless PostgreSQL database
- **Responsive Design**: Works on mobile (375px) to desktop (1920px) viewports
- **Secure API**: JWT verification on every request, ownership validation

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16+ (App Router), React 19+, TypeScript, Tailwind CSS |
| Backend | Python 3.11+, FastAPI, SQLModel, PyJWT |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth with JWT |

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- Neon PostgreSQL account ([Sign up](https://neon.tech))

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Phase-02
git checkout 001-todo-fullstack
```

### 2. Generate JWT Secret

```bash
# macOS/Linux
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

Save this value - you'll need it for both backend and frontend.

### 3. Setup Neon Database

1. Go to [https://console.neon.tech](https://console.neon.tech)
2. Create new project
3. Copy connection string
4. Add `?sslmode=require` to the end

Example: `postgresql://user:pass@ep-host.neon.tech/db?sslmode=require`

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL (from Neon)
# - BETTER_AUTH_SECRET (from step 2)
# - CORS_ORIGINS=http://localhost:3000
```

**Run database migrations**:

```bash
alembic upgrade head
```

**Start backend server**:

```bash
# From backend/ directory
uvicorn src.main:app --reload --port 8000

# Or from project root
cd backend && uvicorn src.main:app --reload --port 8000
```

Backend will run at: [http://localhost:8000](http://localhost:8000)
API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Frontend Setup

**Open new terminal** (keep backend running)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local with your values:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - DATABASE_URL (same as backend)
# - BETTER_AUTH_SECRET (same as backend)
# - NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Start frontend server**:

```bash
npm run dev
```

Frontend will run at: [http://localhost:3000](http://localhost:3000)

### 6. Test the Application

1. Go to [http://localhost:3000](http://localhost:3000)
2. Click "Sign Up" and create an account
3. You'll be redirected to the dashboard
4. Create your first task!

## Project Structure

```
Phase-02/
├── backend/                 # FastAPI Backend
│   ├── src/
│   │   ├── models/          # SQLModel entities (User, Task)
│   │   ├── api/             # API endpoints (tasks.py)
│   │   ├── auth/            # JWT verification
│   │   ├── database.py      # DB session management
│   │   ├── config.py        # Settings
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # Next.js Frontend
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities (API client, auth)
│   │   └── hooks/           # React hooks
│   ├── middleware.ts        # Route protection
│   └── package.json         # Node dependencies
│
├── specs/                   # Documentation
│   └── 001-todo-fullstack/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       ├── tasks.md         # Task breakdown
│       ├── data-model.md    # Database schema
│       ├── research.md      # Technical research
│       └── contracts/       # API contracts
│
└── .env.example             # Environment template
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/signin` - Sign in and get JWT token

### Tasks
- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task title
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

All task endpoints require valid JWT token in `Authorization: Bearer <token>` header.

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
BETTER_AUTH_SECRET=<32+ character hex string>
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
BETTER_AUTH_SECRET=<same as backend>
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**⚠️ CRITICAL**: `BETTER_AUTH_SECRET` must be identical in both files!

## Development

### Backend

```bash
cd backend
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

### Database Migrations

```bash
cd backend

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Testing

### Manual Testing Checklist

- [ ] Sign up new user
- [ ] Sign in with existing user
- [ ] Create task
- [ ] View task list
- [ ] Mark task as complete
- [ ] Edit task title
- [ ] Delete task
- [ ] Sign out and verify tasks persist after sign in
- [ ] Create second user and verify task isolation
- [ ] Test responsive design on mobile viewport (375px)

### User Isolation Verification

1. Create User A with some tasks
2. Sign out
3. Create User B
4. Verify User B cannot see User A's tasks
5. Sign in as User A again
6. Verify User A's tasks are still there

## Architecture

### Authentication Flow

```
1. User submits credentials → Better Auth (Next.js)
2. Better Auth validates → Issues JWT token (HS256)
3. Frontend stores token → localStorage
4. API requests include token → Authorization: Bearer <token>
5. Backend verifies signature → Shared BETTER_AUTH_SECRET
6. Backend extracts user_id → From 'sub' claim
7. Backend filters queries → WHERE user_id = <from_token>
8. Response returned → Only if user owns resource
```

### Security Features

- JWT signature verification on every API request
- User isolation at database query level
- Ownership validation before UPDATE/DELETE operations
- 401 Unauthorized for missing/invalid tokens
- 403 Forbidden for unauthorized resource access
- No secrets in source code (environment variables only)

## Troubleshooting

### Backend: "Connection refused" to database

**Solution**: Verify `DATABASE_URL` includes `?sslmode=require` and Neon project is active.

### Frontend: API calls return 401

**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in both `.env` files (no extra spaces).

### "Module not found" errors

**Solution**:
- Backend: Activate virtual environment and run `pip install -r requirements.txt`
- Frontend: Run `npm install`

### Port already in use

**Solution**:
- Backend port 8000: Change port in uvicorn command
- Frontend port 3000: Next.js will automatically try 3001

## Documentation

- **Feature Specification**: `specs/001-todo-fullstack/spec.md`
- **Implementation Plan**: `specs/001-todo-fullstack/plan.md`
- **Data Model**: `specs/001-todo-fullstack/data-model.md`
- **API Contracts**: `specs/001-todo-fullstack/contracts/api-endpoints.md`
- **Quickstart Guide**: `specs/001-todo-fullstack/quickstart.md`

## Development Methodology

This project follows Spec-Driven Development using Spec-Kit Plus:

1. ✅ `/sp.constitution` - Established project principles
2. ✅ `/sp.specify` - Created feature specification
3. ✅ `/sp.plan` - Generated implementation plan
4. ✅ `/sp.tasks` - Broke down into atomic tasks
5. ✅ `/sp.implement` - Generated code via Claude Code

All code generated via Claude Code with zero manual edits (constitutional requirement).

## License

MIT

## Support

For detailed setup instructions, see [quickstart.md](specs/001-todo-fullstack/quickstart.md)
