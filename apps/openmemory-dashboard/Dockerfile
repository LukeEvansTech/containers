# syntax=docker/dockerfile:1
ARG OPENMEMORY_VERSION=1.2.1
ARG NEXT_PUBLIC_API_URL=http://openmemory.ai.svc.cluster.local:8080

FROM node:20-alpine AS builder

ARG OPENMEMORY_VERSION
ARG NEXT_PUBLIC_API_URL

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="OpenMemory Dashboard - Web UI for OpenMemory"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.version="${OPENMEMORY_VERSION}"
LABEL io.artifacthub.package.readme-url="https://raw.githubusercontent.com/CaviraOSS/OpenMemory/main/dashboard/README.md"
LABEL upstream.version="${OPENMEMORY_VERSION}"
LABEL upstream.source="https://github.com/CaviraOSS/OpenMemory"

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    curl \
    bash \
    git

# Clone OpenMemory repository at specified version
RUN git clone --depth 1 --branch ${OPENMEMORY_VERSION} https://github.com/CaviraOSS/OpenMemory.git /build

# Install dependencies and build dashboard
WORKDIR /build/dashboard

# Set Next.js public env vars for build time
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Install all dependencies (including devDependencies needed for build)
# Use npm install instead of npm ci for better compatibility
RUN npm install --legacy-peer-deps
RUN npm run build

# Production stage
FROM node:20-alpine

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="OpenMemory Dashboard - Web UI for OpenMemory"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

WORKDIR /app

# Copy all necessary files for Next.js production
COPY --from=builder --chown=appuser:appuser /build/dashboard/.next ./.next
COPY --from=builder --chown=appuser:appuser /build/dashboard/public ./public
COPY --from=builder --chown=appuser:appuser /build/dashboard/package.json ./package.json
COPY --from=builder --chown=appuser:appuser /build/dashboard/package-lock.json ./package-lock.json
COPY --from=builder --chown=appuser:appuser /build/dashboard/next.config.ts ./next.config.ts

# Install production dependencies
# Include typescript since next.config.ts requires it at runtime
RUN npm ci --omit=dev && \
    npm install typescript && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 || r.statusCode === 307 || r.statusCode === 404 ? 0 : 1)})"

CMD ["npm", "start"]
