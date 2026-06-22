FROM docker.elastic.co/logstash/logstash:9.1.10

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="Logstash with the Microsoft Sentinel DCR output plugin — OPNsense → Sentinel syslog shipper"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# netbase fixes the JNR `getprotobyname_r failed` regression on slim Ubuntu bases
# (documented known issue for the Microsoft Sentinel Logstash output plugin).
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends netbase \
    && rm -rf /var/lib/apt/lists/*
USER logstash

# Microsoft-supported output plugin → Azure Monitor Logs Ingestion API (DCR-based).
# Version pinned; v2.1.0 is the current release. Logstash 9.1.10 is a plugin-supported version.
RUN logstash-plugin install --version 2.1.0 microsoft-sentinel-log-analytics-logstash-output-plugin

# The pipeline (.conf) and logstash.yml are mounted at runtime via ConfigMap from the
# talos-cluster Flux app (kubernetes/apps/security/opnsense-syslog). No pipeline baked in.
