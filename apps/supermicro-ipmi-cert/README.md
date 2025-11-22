# Supermicro IPMI Certificate Deployer

Container for deploying SSL certificates to modern Supermicro IPMI interfaces using the Redfish API.

## Supported Hardware

- **X12** motherboards with Redfish API
- **X13** motherboards with Redfish API
- **H13** motherboards with Redfish API

**Note**: This version only supports modern Supermicro boards with Redfish API. Legacy X9/X10/X11 support has been removed for simplicity.

## Usage with Cert Warden

### 1. Build and Push Container

```bash
docker build -t ghcr.io/lukevanstech/supermicro-ipmi-cert:latest .
docker push ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

### 2. Configure in Cert Warden

In Cert Warden's certificate post-processing settings, configure the container with these environment variables:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CERTIFICATE_PEM` | Yes | Certificate from Cert Warden | `{{CERTIFICATE_PEM}}` |
| `PRIVATE_KEY_PEM` | Yes | Private key from Cert Warden | `{{PRIVATE_KEY_PEM}}` |
| `IPMI_URL` | Yes | IPMI interface URL | `https://ipmi.example.com` |
| `IPMI_MODEL` | Yes | Board model | `X12` |
| `IPMI_USERNAME` | Yes | IPMI admin username | `ADMIN` |
| `IPMI_PASSWORD` | Conditional | IPMI password (or use `IPMI_PASSWORD_ENV`) | `password123` |
| `IPMI_PASSWORD_ENV` | Conditional | Name of env var containing password | `IPMI_SECRET` |
| `IPMI_NO_REBOOT` | No | Skip IPMI reboot (default: false) | `false` |

### 3. Example Cert Warden Configuration

```yaml
# Post-processing binary configuration
binary: /usr/local/bin/supermicro-ipmi-cert

# Environment variables
environment_variables:
  CERTIFICATE_PEM: "{{CERTIFICATE_PEM}}"
  PRIVATE_KEY_PEM: "{{PRIVATE_KEY_PEM}}"
  IPMI_URL: "https://ipmi-host-01.example.com"
  IPMI_MODEL: "X12"
  IPMI_USERNAME: "ADMIN"
  IPMI_PASSWORD_ENV: "IPMI_PASSWORD"  # Fetch from Kubernetes secret
  IPMI_NO_REBOOT: "false"
```

### 4. Kubernetes Secret for Password

Store IPMI credentials securely:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ipmi-credentials
  namespace: infrastructure
type: Opaque
stringData:
  IPMI_PASSWORD: "your-secure-password"
```

Reference in Cert Warden deployment:

```yaml
envFrom:
  - secretRef:
      name: ipmi-credentials
```

## Manual Testing

Test the container directly:

```bash
docker run --rm \
  -e IPMI_URL="https://192.168.1.100" \
  -e IPMI_MODEL="X12" \
  -e IPMI_USERNAME="ADMIN" \
  -e IPMI_PASSWORD="password" \
  -e CERTIFICATE_PEM="$(cat fullchain.pem)" \
  -e PRIVATE_KEY_PEM="$(cat privkey.pem)" \
  ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

## How It Works

1. Receives certificate data from Cert Warden via environment variables
2. Authenticates to IPMI using provided credentials
3. Uploads certificate and private key
4. Optionally reboots IPMI to apply changes
5. Verifies deployment and reports status

## Security Considerations

- Runs as non-root user (UID 65534)
- No certificate data persisted to disk
- SSL certificate verification disabled for IPMI connections (required for self-signed IPMI certs)
- Credentials passed via environment variables only

## Troubleshooting

### Login Failures

- Verify credentials are correct
- Check network connectivity to IPMI interface
- Ensure IPMI web interface is accessible

### Certificate Upload Failures

- Verify model is correct (X9/X10/X11/X12/X13/H13)
- Check certificate format (PEM)
- Ensure certificate and key match

### Reboot Issues

- Some IPMI versions may fail reboot via API
- Manually reboot IPMI if automatic reboot fails
- Use `IPMI_NO_REBOOT=true` and reboot manually

## Credits

Based on [Jari Turkia's ipmi-updater.py](https://github.com/jturkia/supermicro-ipmi-updater) and adapted for Cert Warden post-processing.

## License

GPL v2 (inherited from original ipmi-updater.py)
