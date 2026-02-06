# Todo App Frontend

Modern Next.js 16+ frontend with App Router, JWT authentication, and task management.

## Features

- **Authentication**: JWT-based authentication with FastAPI backend
- **Task Management**: Create, read, update, delete, and complete tasks
- **Responsive Design**: Mobile-first design (375px to 1920px)
- **Modern Stack**: Next.js 16+, React 19, TypeScript, Tailwind CSS
- **Server Components**: Optimized with Server and Client Components
- **Error Handling**: Comprehensive error boundaries and 401 handling

## Getting Started

### Prerequisites

- Node.js 20+
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth route group (signin, signup)
│   │   ├── dashboard/         # Protected dashboard routes
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── task-list.tsx
│   │   ├── task-item.tsx
│   │   ├── task-form.tsx
│   │   └── confirm-dialog.tsx
│   ├── hooks/                 # Custom React hooks
│   │   └── use-auth.ts
│   └── lib/                   # Utilities
│       ├── api/               # API clients
│       │   ├── client.ts      # Base API client
│       │   ├── tasks.ts       # Task operations
│       │   └── error-handler.ts
│       └── auth/              # Authentication
│           ├── better-auth.ts # Auth functions
│           └── session.ts     # Token storage
├── middleware.ts              # Route protection
├── tailwind.config.ts         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── package.json
```

## Key Files

### Authentication
- `src/lib/auth/better-auth.ts` - Auth functions (signin, signup, signout)
- `src/lib/auth/session.ts` - Token storage utilities
- `src/hooks/use-auth.ts` - Auth React hook
- `middleware.ts` - Route protection middleware

### Task Management
- `src/lib/api/tasks.ts` - Task API client
- `src/components/task-list.tsx` - Task list component
- `src/components/task-item.tsx` - Individual task with edit/delete
- `src/components/task-form.tsx` - Create task form

### Pages
- `src/app/page.tsx` - Landing page
- `src/app/(auth)/signin/page.tsx` - Sign in page
- `src/app/(auth)/signup/page.tsx` - Sign up page
- `src/app/dashboard/page.tsx` - Main dashboard

## API Integration

The frontend integrates with FastAPI backend at `http://localhost:8000`:

### Authentication Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Sign in user

### Task Endpoints
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task title
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

All authenticated requests include JWT token in `Authorization: Bearer <token>` header.

## Features Implementation

### User Authentication (US1)
- Sign up with email/password
- Sign in with credentials
- JWT token storage in localStorage
- Automatic 401 handling and redirect
- Route protection middleware

### Task Management (US2-US4)
- Create tasks with title validation
- View tasks ordered by newest first
- Edit task titles inline
- Toggle completion with checkbox
- Delete tasks with confirmation dialog
- Empty state when no tasks

### Responsive Design (US5)
- Mobile-first Tailwind CSS
- Breakpoints: 375px (mobile), 768px (tablet), 1920px (desktop)
- Flexible grid layouts
- Touch-friendly buttons

## Testing

To test the application:

1. Start backend: `cd backend && uvicorn src.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to `http://localhost:3000`
4. Sign up for a new account
5. Create, edit, complete, and delete tasks

## Deployment

### Vercel (Recommended)

```bash
vercel deploy
```

Set environment variables in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` - Production API URL
- `NEXT_PUBLIC_APP_URL` - Production frontend URL

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### 401 Errors
- Check backend is running on `http://localhost:8000`
- Verify JWT token is stored in localStorage
- Check token hasn't expired (24h default)

### CORS Issues
- Ensure backend CORS allows `http://localhost:3000`
- Check `NEXT_PUBLIC_API_URL` environment variable

### Build Errors
- Run `npm install` to ensure dependencies are installed
- Check Node.js version (20+)
- Clear `.next` folder and rebuild

## License

MIT
