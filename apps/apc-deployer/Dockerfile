FROM python:3.12-alpine AS builder

ARG KUBECTL_VERSION=v1.32.0
ARG APC_TOOL_VERSION=v1.3.3
ARG TARGETARCH=amd64

WORKDIR /downloads

# Download kubectl
RUN wget -q -O kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    chmod +x kubectl

# Download apc-p15-tool
RUN wget -q "https://github.com/gregtwallace/apc-p15-tool/releases/download/${APC_TOOL_VERSION}/apc-p15-tool-${APC_TOOL_VERSION}_linux_${TARGETARCH}.tar.gz" && \
    tar -xzf apc-p15-tool-*.tar.gz && \
    chmod +x apc-p15-tool

# Final runtime image
FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="APC NMC Certificate Deployment Tool for Cert Warden"
LABEL org.opencontainers.image.licenses="GPL-2.0"

# Install runtime dependencies
RUN apk add --no-cache \
    openssh-client \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Copy binaries from builder
COPY --from=builder /downloads/kubectl /usr/local/bin/kubectl
COPY --from=builder /downloads/apc-p15-tool /usr/local/bin/apc-p15-tool

# Create app directory and set permissions for nobody user (65534:65534)
RUN mkdir -p /app/scripts && \
    chown -R nobody:nobody /app

# Copy application
COPY apc_updater.py /app/scripts/apc_updater.py
RUN chmod +x /app/scripts/apc_updater.py && \
    chown nobody:nobody /app/scripts/apc_updater.py

# Switch to non-root nobody user
USER nobody

WORKDIR /app

# Verify installations
RUN kubectl version --client && \
    apc-p15-tool version || echo "apc-p15-tool installed" && \
    python3 -c "import sys; print(f'Python {sys.version}')"

# Default command
CMD ["/bin/sh"]
