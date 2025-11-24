# syntax=docker/dockerfile:1
ARG OPENMEMORY_VERSION=1.2.1

FROM node:20-alpine AS builder

ARG OPENMEMORY_VERSION

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="OpenMemory - Long-term memory engine for AI"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.version="${OPENMEMORY_VERSION}"
LABEL io.artifacthub.package.readme-url="https://raw.githubusercontent.com/CaviraOSS/OpenMemory/main/README.md"
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

# Install Bun
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone OpenMemory repository at specified version
RUN git clone --depth 1 --branch ${OPENMEMORY_VERSION} https://github.com/CaviraOSS/OpenMemory.git /build

# Install dependencies, build, and prune
WORKDIR /build/backend
RUN bun install --concurrent-scripts=1 --concurrent-io=50 && \
    bun run build && \
    npm prune --production

# Production stage
FROM node:20-alpine

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="OpenMemory - Long-term memory engine for AI"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

WORKDIR /app

# Copy built application
COPY --from=builder --chown=appuser:appuser /build/backend/node_modules ./node_modules
COPY --from=builder --chown=appuser:appuser /build/backend/dist ./dist
COPY --from=builder --chown=appuser:appuser /build/backend/package.json ./

# Create data directory with proper permissions
RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app/data && \
    chmod 755 /app/data

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8080/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["npm", "start"]
