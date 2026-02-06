# Use Node.js 20 LTS as the base image
FROM node:20-alpine AS base

# Set build args to allow customization
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/44cd7b6a37ee6bca6f98bf5a70bc9c83afac49d6#nodealpine
# to understand why libc6-compat might be needed
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci


# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line to disable telemetry at build time
ENV NEXT_TELEMETRY_DISABLED 1

# Copy environment variables if available
COPY .env.local* .env* ./

# Build the Next.js application
RUN npm run build


# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Uncomment the following line to disable telemetry at runtime
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy package.json
COPY package.json .

# You only need to copy next.config.ts if you are NOT using the default configuration
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the built Next.js app from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next

# Copy source code for development
COPY --from=builder /app/src ./src

USER nextjs

EXPOSE 3000

ENV PORT 3000

# Run the application - try server.js if it exists, otherwise start normally
CMD ["sh", "-c", "if [ -f server.js ]; then node server.js; else npx next start --port $PORT; fi"]