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

# Create non-root user (use existing nobody user)
# Alpine already has nobody:nobody (65534:65534)
RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app

# Copy application
COPY supermicro_ipmi_cert.py /app/supermicro_ipmi_cert.py
RUN chmod +x /app/supermicro_ipmi_cert.py && \
    chown -R app:app /app

# Switch to non-root user
USER app

WORKDIR /app

ENTRYPOINT ["python3", "/app/supermicro_ipmi_cert.py"]
