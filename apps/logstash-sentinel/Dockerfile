FROM docker.elastic.co/logstash/logstash:9.1.10

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="Logstash with the Microsoft Sentinel DCR output plugin — OPNsense → Sentinel syslog shipper"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# No netbase/getprotobyname workaround needed: the Logstash 9.x base is UBI9 (rhel 9.7), which
# already ships /etc/protocols + /etc/services via the `setup` rpm (verified — getent resolves).
# The old apt-get netbase fix only applied to the slim-Ubuntu bases Elastic used pre-9.x (and there
# is no apt-get on UBI). Microsoft-supported output plugin → Azure Monitor Logs Ingestion API (DCR).
# Version pinned; v2.1.0 is the current release. Logstash 9.1.10 is a plugin-supported version.
RUN logstash-plugin install --version 2.1.0 microsoft-sentinel-log-analytics-logstash-output-plugin

# The pipeline (.conf) and logstash.yml are mounted at runtime via ConfigMap from the
# talos-cluster Flux app (kubernetes/apps/security/sentinel-syslog). No pipeline baked in.
