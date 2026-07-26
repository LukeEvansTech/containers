FROM alpine:3.22@sha256:14358309a308569c32bdc37e2e0e9694be33a9d99e68afb0f5ff33cc1f695dce AS builder

ARG KUBECTL_VERSION=v1.32.0
ARG BROTHER_CERT_VERSION=v0.3.0
ARG TARGETARCH=amd64

WORKDIR /downloads

# Download kubectl
RUN wget -q -O kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    chmod +x kubectl

# Download brother-cert
RUN wget -q "https://github.com/gregtwallace/brother-cert/releases/download/${BROTHER_CERT_VERSION}/brother-cert-${BROTHER_CERT_VERSION}_linux_${TARGETARCH}.tar.gz" && \
    tar -xzf brother-cert-*.tar.gz && \
    chmod +x brother-cert

# Final runtime image
FROM alpine:3.22@sha256:14358309a308569c32bdc37e2e0e9694be33a9d99e68afb0f5ff33cc1f695dce

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="Brother Printer Certificate Deployment Tool for Cert Warden"
LABEL org.opencontainers.image.licenses="GPL-2.0"

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Copy binaries from builder
COPY --from=builder /downloads/kubectl /usr/local/bin/kubectl
COPY --from=builder /downloads/brother-cert /usr/local/bin/brother-cert

# Create app directory and set permissions for nobody user (65534:65534)
RUN mkdir -p /app && \
    chown -R nobody:nobody /app

# Switch to non-root nobody user
USER nobody

WORKDIR /app

# Verify installations
RUN kubectl version --client && \
    brother-cert --version || echo "brother-cert installed"

# Default command
CMD ["/bin/sh"]
