<div align="center">

## Containers

_Container images for home infrastructure certificate management_

</div>

<div align="center">

![GitHub Repo stars](https://img.shields.io/github/stars/LukeEvansTech/containers?style=for-the-badge)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/LukeEvansTech/containers/release.yaml?style=for-the-badge&label=Release)

</div>

Welcome to my container images! These are purpose-built containers for automated certificate deployment to various hardware devices, designed to work with [Cert Warden](https://www.certwarden.com/) post-processing.

## Available Containers

| Container | Description | Architectures |
|-----------|-------------|---------------|
| [supermicro-ipmi-cert](./apps/supermicro-ipmi-cert) | Deploy certificates to Supermicro IPMI interfaces (X9, X10, X11, X12, X13, H13) | `linux/amd64`, `linux/arm64` |

## Mission Statement

This repository provides specialized post-processing containers for [Cert Warden](https://www.certwarden.com/), enabling automated certificate deployment to hardware devices that don't have native certificate management integrations.

Each container:
- Accepts certificate data via environment variables
- Authenticates to the target device
- Deploys the certificate securely
- Reports success/failure for monitoring

## Usage with Cert Warden

These containers are designed to run as [Cert Warden post-processing binaries](https://www.certwarden.com/docs/using_certificates/post_process_bin/). Configure them in Cert Warden's certificate settings:

1. Build and push the container to your registry
2. In Cert Warden, configure post-processing for a certificate
3. Set environment variables for device credentials and configuration
4. Cert Warden will automatically trigger the container after certificate renewal

Example configuration:
```yaml
# In Cert Warden post-processing settings
binary: /path/to/container-binary
environment_variables:
  CERTIFICATE_PEM: "{{CERTIFICATE_PEM}}"
  PRIVATE_KEY_PEM: "{{PRIVATE_KEY_PEM}}"
  DEVICE_URL: "https://ipmi.example.com"
  DEVICE_USERNAME: "ADMIN"
  DEVICE_PASSWORD_ENV: "IPMI_PASSWORD"
```

## Building Containers

Each container can be built individually:

```bash
cd apps/supermicro-ipmi-cert
docker build -t ghcr.io/lukevanstech/supermicro-ipmi-cert:latest .
docker push ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

## Contributing

Contributions are welcome! If you have additional hardware devices that need certificate management, follow this pattern:

1. Create a new directory in `apps/`
2. Include a `Dockerfile`, deployment script, and `README.md`
3. Test with Cert Warden
4. Submit a PR

## Credits

- Built on patterns from [home-operations/containers](https://github.com/home-operations/containers)
- Inspired by [gregtwallace/certwarden](https://github.com/gregtwallace/certwarden) post-processing plugins
- IPMI update logic adapted from [Jari Turkia's ipmi-updater.py](https://github.com/jturkia/supermicro-ipmi-updater)

## License

See [LICENSE](./LICENSE) file for details.
