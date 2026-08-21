# The published image tag comes from apps/logstash-sentinel/VERSION — a Renovate custom
# manager keeps it in lockstep with this FROM tag. A stale VERSION ships a tag that lies
# about the Logstash inside (9.1.10-tagged images carried 9.4.x/9.5.x for four days).
FROM docker.elastic.co/logstash/logstash:9.5.2@sha256:4a49af2d3798aeccc88cf02935af3c71535bff8d9d0d5e9fc1205d92dc837bc4

LABEL org.opencontainers.image.source="https://github.com/LukeEvansTech/containers"
LABEL org.opencontainers.image.description="Logstash with the Microsoft Sentinel DCR output plugin — OPNsense → Sentinel syslog shipper"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# No netbase/getprotobyname workaround needed: the Logstash 9.x base is UBI9 (rhel 9.7), which
# already ships /etc/protocols + /etc/services via the `setup` rpm (verified — getent resolves).
# The old apt-get netbase fix only applied to the slim-Ubuntu bases Elastic used pre-9.x (and there
# is no apt-get on UBI). Microsoft-supported output plugin → Azure Monitor Logs Ingestion API (DCR).
# Version pinned; a Renovate rubygems custom manager tracks it. 2.x is the Java rewrite of the
# plugin. 2.1.0 INSTALLS fine but fails to LOAD under the JRuby 10 (Ruby 3.4) runtime that
# Logstash 9.4+ ships — pipeline creation dies with "Couldn't find any output plugin named
# 'microsoft-sentinel-log-analytics-logstash-output-plugin'" (a LoadError wearing a not-installed
# message) — which crashlooped the talos-cluster shipper on every rebuild after the 9.1.10 → 9.4.4
# base bump. 2.5.0 verified starting cleanly against this exact base image in-cluster.
RUN logstash-plugin install --version 2.5.0 microsoft-sentinel-log-analytics-logstash-output-plugin

# The pipeline (.conf) and logstash.yml are mounted at runtime via ConfigMap from the
# talos-cluster Flux app (kubernetes/apps/security/sentinel-syslog). No pipeline baked in.
