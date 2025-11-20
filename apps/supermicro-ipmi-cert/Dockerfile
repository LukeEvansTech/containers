FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="Supermicro IPMI Certificate Deployment Tool for Cert Warden"
LABEL org.opencontainers.image.licenses="GPL-2.0"

# Install dependencies
RUN apk add --no-cache \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Install Python packages
RUN pip install --no-cache-dir \
    requests==2.31.0

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

ENTRYPOINT ["python3", "/app/supermicro_ipmi_cert.py"]
