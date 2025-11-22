# APC NMC Certificate Deployer

Container for deploying SSL certificates to APC Network Management Cards (NMC) via SSH using the [apc-p15-tool](https://github.com/gregtwallace/apc-p15-tool).

## Supported Devices

- APC UPS with Network Management Cards
- Supports both modern and legacy APC devices with cryptlib SSH

## Features

- Automated certificate deployment via apc-p15-tool
- Support for legacy APC devices with `--insecurecipher` flag
- Non-root container execution (runs as nobody:nobody)
- Pre-installed kubectl for Kubernetes integration
- Detailed logging and error reporting

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APC_HOSTNAME` | Yes | APC NMC hostname or IP address |
| `APC_USERNAME` | Yes | APC admin username |
| `APC_PASSWORD` | Yes | APC admin password |
| `APC_FINGERPRINT` | Yes | SSH host key fingerprint (SHA256) |
| `APC_INSECURE_CIPHER` | No | Set to `true` for legacy devices (default: `false`) |
| `CERTIFICATE_PEM` | Yes | Certificate in PEM format |
| `PRIVATE_KEY_PEM` | Yes | Private key in PEM format |

## Usage

### Standalone

```bash
docker run --rm \
  -e APC_HOSTNAME="10.0.0.1" \
  -e APC_USERNAME="apc" \
  -e APC_PASSWORD="password" \
  -e APC_FINGERPRINT="SHA256:xxx..." \
  -e CERTIFICATE_PEM="$(cat cert.pem)" \
  -e PRIVATE_KEY_PEM="$(cat key.pem)" \
  ghcr.io/lukeevanstech/apc-deployer:latest \
  python3 /app/scripts/apc_updater.py \
    --hostname "${APC_HOSTNAME}" \
    --username "${APC_USERNAME}" \
    --password "${APC_PASSWORD}" \
    --fingerprint "${APC_FINGERPRINT}" \
    --cert-file /tmp/cert.pem \
    --key-file /tmp/key.pem \
    --apc-tool-path /usr/local/bin/apc-p15-tool \
    --debug
```

### With Cert Warden

This container is designed to be used with Cert Warden's post-processing feature. The certificate data is passed via environment variables automatically.

### Kubernetes Job

See the talos-cluster repository for complete Kubernetes Job examples that use this container with ExternalSecrets for credential management.

## Getting SSH Fingerprint

For legacy APC devices with cryptlib SSH:

```bash
ssh -o KexAlgorithms=+diffie-hellman-group1-sha1,diffie-hellman-group14-sha1 \
    -o HostKeyAlgorithms=+ssh-rsa \
    -o PubkeyAcceptedAlgorithms=+ssh-rsa \
    -v apc@<APC_IP> exit 2>&1 | grep "Server host key"
```

## Building

```bash
docker build -t ghcr.io/lukeevanstech/apc-deployer:latest .
docker push ghcr.io/lukeevanstech/apc-deployer:latest
```

## Image Size

Approximately 120-130MB

## Security

- Runs as non-root user (nobody:nobody)
- Multi-stage build for minimal attack surface
- No unnecessary packages installed
- Uses official Python Alpine base image

## Credits

- [apc-p15-tool](https://github.com/gregtwallace/apc-p15-tool) by Greg Wallace
- Certificate deployment pattern from Cert Warden documentation

## License

GPL-2.0
