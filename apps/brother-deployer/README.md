# Brother Printer Certificate Deployer

Container for deploying SSL certificates to Brother network printers using the [brother-cert](https://github.com/gregtwallace/brother-cert) tool.

## Supported Devices

- Brother network printers with web interface
- Requires printer to support SSL certificate management

## Features

- Automated certificate deployment via brother-cert tool
- Non-root container execution (runs as nobody:nobody)
- Pre-installed kubectl for Kubernetes integration
- Minimal Alpine-based image

## Environment Variables

When using with Cert Warden, the container uses brother-cert command-line arguments.

## Usage

### Standalone

```bash
docker run --rm \
  -v /path/to/certs:/certs:ro \
  ghcr.io/lukeevanstech/brother-deployer:latest \
  brother-cert \
    --hostname "10.0.0.1" \
    --password "password" \
    --keyfile /certs/key.pem \
    --certfile /certs/cert.pem
```

### With Cert Warden

This container is designed to be used with Cert Warden's post-processing feature. The Kubernetes Job mounts certificates as files and reads configuration from Kubernetes Secrets.

### Kubernetes Job

See the talos-cluster repository for complete Kubernetes Job examples that use this container with ExternalSecrets for credential management.

## Command-Line Arguments

The container uses the `brother-cert` tool which accepts:

| Argument | Required | Description |
|----------|----------|-------------|
| `--hostname` | Yes | Brother printer hostname or IP address |
| `--password` | Yes | Brother printer admin password |
| `--keyfile` | Yes | Path to X.509 private key file |
| `--certfile` | Yes | Path to X.509 certificate file |
| `--version` | No | Display version information |

## Building

```bash
docker build -t ghcr.io/lukeevanstech/brother-deployer:latest .
docker push ghcr.io/lukeevanstech/brother-deployer:latest
```

## Image Size

Approximately 80-90MB

## Security

- Runs as non-root user (nobody:nobody)
- Multi-stage build for minimal attack surface
- No unnecessary packages installed
- Uses official Alpine base image

## Credits

- [brother-cert](https://github.com/gregtwallace/brother-cert) by Greg Wallace
- Certificate deployment pattern from Cert Warden documentation

## License

GPL-2.0

## Version

Current version: v0.3.0 (uses brother-cert v0.3.0)
