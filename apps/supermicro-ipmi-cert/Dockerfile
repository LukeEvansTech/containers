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
LABEL org.opencontainers.image.description="Supermicro IPMI Certificate Deployment Tool for Cert Warden (Redfish/X12/X13/H13 only)"
LABEL org.opencontainers.image.licenses="GPL-2.0"

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Copy kubectl from builder
COPY --from=builder /downloads/kubectl /usr/local/bin/kubectl

# Install Python packages
RUN pip install --no-cache-dir \
    requests==2.32.3 \
    pyOpenSSL==24.3.0

# Create app directory and set permissions for nobody user (65534:65534)
# Alpine already has nobody:nobody (65534:65534) user
RUN mkdir -p /app && \
    chown -R nobody:nobody /app

# Copy application
COPY supermicro_ipmi_cert.py /app/supermicro_ipmi_cert.py
RUN chmod +x /app/supermicro_ipmi_cert.py && \
    chown nobody:nobody /app/supermicro_ipmi_cert.py

# Switch to non-root nobody user
USER nobody

WORKDIR /app

# Verify installations
RUN kubectl version --client && \
    python3 -c "import requests; import OpenSSL; print(f'Python packages OK')"

ENTRYPOINT ["python3", "/app/supermicro_ipmi_cert.py"]
