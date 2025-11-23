# Build argument para determinar se é produção
ARG BUILD_TARGET=development

# ============================================
# STAGE 1: Builder (para produção)
# ============================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (incluindo dev para build)
RUN npm ci

# Copy application files
COPY . .

# Build application
RUN npm run build

# ============================================
# STAGE 2: Production
# ============================================
FROM node:18-alpine AS production

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Install wget for healthcheck (before switching user)
RUN apk add --no-cache wget

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/package.json ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app

USER nextjs

# Set environment to production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3002 || exit 1

# Expose port
EXPOSE 3002

# Start application (Next.js usa PORT env var automaticamente)
CMD ["npm", "start"]

# ============================================
# STAGE 3: Development
# ============================================
FROM node:18-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm install

# Copy application files
COPY . .

# Expose port
EXPOSE 3002

# Run development server (Next.js usa variável PORT)
ENV PORT=3002
CMD ["npm", "run", "dev", "--", "-p", "3002"]
