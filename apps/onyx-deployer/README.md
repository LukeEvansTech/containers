# NVIDIA Onyx Switch Certificate Deployer

Container for deploying SSL certificates to NVIDIA Onyx switches via the JSON API.

## Supported Hardware

- **NVIDIA Onyx** switches running version 3.9+ with JSON API enabled
- Tested on Onyx v3.10.4606

## Usage with Cert Warden

### 1. Build and Push Container

```bash
docker build -t ghcr.io/lukevanstech/onyx-deployer:latest .
docker push ghcr.io/lukevanstech/onyx-deployer:latest
```

### 2. Configure in Cert Warden

In Cert Warden's certificate post-processing settings, configure the container with these environment variables:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CERTIFICATE_PEM` | Yes | Certificate from Cert Warden | `{{CERTIFICATE_PEM}}` |
| `PRIVATE_KEY_PEM` | Yes | Private key from Cert Warden | `{{PRIVATE_KEY_PEM}}` |
| `ONYX_HOSTNAME` | Yes | Switch hostname or IP | `10.0.0.1` |
| `ONYX_USERNAME` | Yes | Admin username | `admin` |
| `ONYX_PASSWORD` | Conditional | Password (or use `ONYX_PASSWORD_ENV`) | `password123` |
| `ONYX_PASSWORD_ENV` | Conditional | Name of env var containing password | `ONYX_SECRET` |
| `ONYX_CERT_NAME` | No | Certificate name on switch (default: `custom-cert`) | `my-cert` |
| `ONYX_NO_SAVE` | No | Skip saving config (default: false) | `false` |

### 3. Example Cert Warden Configuration

```yaml
# Post-processing binary configuration
binary: /usr/local/bin/onyx-cert-updater

# Environment variables
environment_variables:
  CERTIFICATE_PEM: "{{CERTIFICATE_PEM}}"
  PRIVATE_KEY_PEM: "{{PRIVATE_KEY_PEM}}"
  ONYX_HOSTNAME: "switch.example.com"
  ONYX_USERNAME: "admin"
  ONYX_PASSWORD_ENV: "ONYX_PASSWORD"  # Fetch from Kubernetes secret
  ONYX_CERT_NAME: "cert-warden-cert"
```

### 4. Kubernetes Secret for Password

Store switch credentials securely:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: onyx-credentials
  namespace: infrastructure
type: Opaque
stringData:
  ONYX_PASSWORD: "your-secure-password"
```

Reference in Cert Warden deployment:

```yaml
envFrom:
  - secretRef:
      name: onyx-credentials
```

## Manual Testing

Test the container directly:

```bash
docker run --rm \
  -e ONYX_HOSTNAME="192.168.1.100" \
  -e ONYX_USERNAME="admin" \
  -e ONYX_PASSWORD="password" \
  -e CERTIFICATE_PEM="$(cat fullchain.pem)" \
  -e PRIVATE_KEY_PEM="$(cat privkey.pem)" \
  ghcr.io/lukevanstech/onyx-deployer:latest
```

Or test with the Python script directly:

```bash
python3 onyx_cert_updater.py \
  --hostname 192.168.1.100 \
  --username admin \
  --password 'your-password' \
  --cert-file /path/to/cert.pem \
  --key-file /path/to/key.pem \
  --cert-name custom-cert
```

## How It Works

1. Receives certificate data from Cert Warden via environment variables
2. Authenticates to Onyx switch using form-based login (session cookie)
3. Uses JSON API to import certificate and private key
4. Sets the imported certificate as the HTTPS certificate
5. Saves configuration (unless `--no-save` is specified)
6. Verifies deployment and reports status

## API Details

The deployer uses the Onyx JSON API:
- **Login**: `POST /admin/launch?script=rh&template=login&action=login`
- **Commands**: `POST /admin/launch?script=rh&template=json-request&action=json-login`

Key commands executed:
```
crypto certificate name <name> public-cert pem "<PEM>"
crypto certificate name <name> private-key pem "<PEM>"
web https certificate name <name>
write memory
```

## Security Considerations

- Runs as non-root user (UID 65534)
- No certificate data persisted to disk
- SSL certificate verification disabled for switch connections (required for self-signed certs)
- Credentials passed via environment variables only

## Troubleshooting

### Login Failures

- Verify credentials are correct
- Check network connectivity to switch management interface
- Ensure the web interface is accessible

### Certificate Import Failures

- Verify certificate format (PEM)
- Ensure certificate and key match
- Check that the certificate name doesn't conflict with existing certificates

### Configuration Save Failures

- Verify admin privileges on the account
- Check switch has available storage for config

### Empty API Response

- The JSON API redirects from `json-login` to `internal-json-login`
- If using curl, ensure `-L` flag is used to follow redirects
- Session cookie must be preserved across requests

## Credits

Developed for Cert Warden certificate automation on NVIDIA/Mellanox Onyx switches.

## License

GPL v2
