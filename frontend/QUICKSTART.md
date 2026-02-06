# Todo App Frontend - Quick Start Guide

## Prerequisites

1. **Node.js 20+** installed
2. **Backend API running** on `http://localhost:8000`
3. **PostgreSQL database** configured for backend

## Setup in 3 Steps

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Step 3: Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## First Use

1. **Sign Up**: Click "Create Account" and register with email/password
2. **Create Tasks**: Add tasks using the form on dashboard
3. **Manage Tasks**: Check to complete, edit title, or delete tasks

## Key Features Implemented

### Authentication (Tasks T020-T029)
- JWT authentication with FastAPI backend
- Sign up and sign in pages
- Automatic token storage in localStorage
- Route protection middleware
- 401 error handling with automatic redirect

### Task Management (Tasks T033-T047)
- Dashboard with task list
- Create tasks with title validation
- Edit task titles inline
- Toggle completion with checkbox
- Delete tasks with confirmation dialog
- Empty state for no tasks
- Loading states and error handling

### Responsive Design (Tasks T048-T052)
- Mobile-first Tailwind CSS
- Responsive grid layouts
- Touch-friendly buttons
- Breakpoints: 375px, 768px, 1920px

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/              # Sign in/up pages (route group)
│   │   │   ├── layout.tsx       # Auth layout
│   │   │   ├── signin/page.tsx  # Sign in page
│   │   │   └── signup/page.tsx  # Sign up page
│   │   ├── dashboard/           # Protected dashboard
│   │   │   ├── layout.tsx       # Dashboard layout with nav
│   │   │   ├── page.tsx         # Main task management page
│   │   │   ├── loading.tsx      # Loading skeleton
│   │   │   └── error.tsx        # Error boundary
│   │   ├── layout.tsx           # Root layout (metadata)
│   │   ├── page.tsx             # Landing page
│   │   ├── not-found.tsx        # 404 page
│   │   └── globals.css          # Global Tailwind styles
│   ├── components/
│   │   ├── task-list.tsx        # Task list with empty state
│   │   ├── task-item.tsx        # Individual task (edit/delete)
│   │   ├── task-form.tsx        # Create task form
│   │   └── confirm-dialog.tsx   # Delete confirmation modal
│   ├── hooks/
│   │   └── use-auth.ts          # Auth hook (signin/signup/signout)
│   └── lib/
│       ├── api/
│       │   ├── client.ts        # Base API client with JWT
│       │   ├── tasks.ts         # Task CRUD operations
│       │   └── error-handler.ts # Error handling utilities
│       └── auth/
│           ├── better-auth.ts   # Auth functions
│           └── session.ts       # Token storage
├── middleware.ts                # Route protection
├── .env.local                   # Environment variables
├── package.json                 # Dependencies
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
└── next.config.ts               # Next.js configuration
```

## API Endpoints Used

### Authentication
- `POST /api/auth/signup` - Register user
- `POST /api/auth/signin` - Authenticate user

### Tasks (Require JWT Token)
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task title
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

## Testing the Application

### 1. Authentication Flow
```bash
# Start app
npm run dev

# Navigate to http://localhost:3000
# Click "Create Account"
# Enter email: test@example.com, password: password123
# Should redirect to /dashboard
```

### 2. Task Management
```bash
# On dashboard:
# 1. Create task: "Buy groceries"
# 2. Check checkbox to complete
# 3. Click edit icon to modify title
# 4. Click delete icon and confirm
```

### 3. Responsive Design
```bash
# Open Chrome DevTools (F12)
# Toggle device toolbar (Ctrl+Shift+M)
# Test viewports:
# - iPhone SE (375px)
# - iPad (768px)
# - Desktop (1920px)
```

## Common Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## Troubleshooting

### Backend Not Running
```
Error: "Failed to fetch"
Solution: Start backend with `cd backend && uvicorn src.main:app --reload`
```

### 401 Unauthorized
```
Solution: Token expired or invalid
- Sign out and sign in again
- Check backend JWT secret matches
- Verify token in localStorage (DevTools > Application)
```

### CORS Errors
```
Solution: Backend must allow frontend origin
- Check backend CORS configuration includes http://localhost:3000
- Restart backend after config changes
```

### Build Errors
```
Solution: Clean and reinstall
npm run clean
rm -rf node_modules .next
npm install
npm run build
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_APP_URL` | Yes | `http://localhost:3000` | Frontend URL |

## Security Notes

- JWT tokens stored in localStorage
- Tokens automatically attached to API requests
- 401 errors trigger automatic signout
- Protected routes require authentication
- Middleware enforces route protection

## Next Steps

1. **Deploy Backend**: Deploy FastAPI to production
2. **Deploy Frontend**: Deploy to Vercel/Netlify
3. **Update Environment Variables**: Set production URLs
4. **Test End-to-End**: Verify full user flow works

## Support

For issues or questions:
1. Check backend logs: Backend console
2. Check frontend logs: Browser DevTools Console
3. Review API endpoints: `http://localhost:8000/docs`

## Task Completion Status

All frontend tasks completed:

**Authentication (US1)**
- [x] T020: Configure Better Auth
- [x] T021: Better Auth API route (not needed - using FastAPI directly)
- [x] T022: useAuth hook
- [x] T023: Signup page
- [x] T024: Signin page
- [x] T025: Auth layout
- [x] T026: Middleware
- [x] T027: Landing page
- [x] T028: Root layout
- [x] T029: Error handler

**Task Management (US2-US4)**
- [x] T033: Dashboard layout
- [x] T034: Dashboard page
- [x] T035: TaskList component
- [x] T036: TaskItem component
- [x] T037: TaskForm component
- [x] T038: Task API client
- [x] T041: Edit mode in TaskItem
- [x] T042: Completion checkbox
- [x] T045: Delete button
- [x] T046: ConfirmDialog component
- [x] T047: Delete method in API client

**Responsive Design (US5)**
- [x] T048-T052: All components responsive with Tailwind CSS

## Ready to Use!

The frontend is fully functional and ready to use with the FastAPI backend. Enjoy managing your tasks!
