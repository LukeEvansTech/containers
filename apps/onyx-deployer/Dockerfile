FROM python:3.12-alpine AS builder

ARG KUBECTL_VERSION=v1.32.0
ARG TARGETARCH=amd64

WORKDIR /downloads

# Download kubectl
RUN wget -q -O kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    chmod +x kubectl

# Final runtime image
FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="NVIDIA Onyx Switch Certificate Deployment Tool for Cert Warden"
LABEL org.opencontainers.image.licenses="GPL-2.0"

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    openssl \
    && rm -rf /var/cache/apk/*

# Copy kubectl from builder
COPY --from=builder /downloads/kubectl /usr/local/bin/kubectl

# Install Python packages (pyOpenSSL optional for cert parsing)
RUN pip install --no-cache-dir \
    pyOpenSSL==24.3.0

# Create app directory and set permissions for nobody user (65534:65534)
# Alpine already has nobody:nobody (65534:65534) user
RUN mkdir -p /app && \
    chown -R nobody:nobody /app

# Copy application
COPY onyx_cert_updater.py /app/onyx_cert_updater.py
RUN chmod +x /app/onyx_cert_updater.py && \
    chown nobody:nobody /app/onyx_cert_updater.py

# Switch to non-root nobody user
USER nobody

WORKDIR /app

# Verify installations
RUN kubectl version --client && \
    python3 -c "import urllib.request; print('Python stdlib OK')" && \
    python3 -c "import OpenSSL; print('pyOpenSSL OK')"

ENTRYPOINT ["python3", "/app/onyx_cert_updater.py"]
