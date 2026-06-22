# logstash-sentinel

Logstash with the **Microsoft Sentinel Logstash output plugin**
(`microsoft-sentinel-log-analytics-logstash-output-plugin`, v2.1.0) baked in.

Used as the in-cluster **OPNsense → Microsoft Sentinel** syslog shipper: a `syslog` input receives
OPNsense logs, the pipeline filters hard, and the output plugin POSTs to the Azure Monitor **Logs
Ingestion API** against a DCR — landing in the standard **Syslog** table on the management LAW.

- Base: `docker.elastic.co/logstash/logstash:9.1.10` (a plugin-supported Logstash version).
- `netbase` added to avoid the JNR `getprotobyname_r failed` regression on slim Ubuntu bases.
- Pipeline + `logstash.yml` are **not** baked in — they're mounted via ConfigMap by the Flux app
  in `LukeEvansTech/talos-cluster` (`kubernetes/apps/security/opnsense-syslog`).

Image: `ghcr.io/lukeevanstech/logstash-sentinel`

Design / rationale: `codelooksazurelandingzone/2026-06-18-opnsense-sentinel-ingestion-spec.md`.
