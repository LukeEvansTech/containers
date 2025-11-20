# CI/CD Setup & Usage

This repository uses GitHub Actions to automatically build and push container images to GitHub Container Registry (GHCR).

## GitHub Container Registry

**Good news**: GHCR is automatically available for your GitHub account! No separate setup required.

Your containers will be published to: `ghcr.io/lukevanstech/<app-name>`

## Initial Repository Setup

### 1. Enable Package Permissions

The workflow uses `GITHUB_TOKEN` to push to GHCR. You need to grant write permissions:

1. Go to your repo: https://github.com/LukeEvansTech/containers/settings/actions
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
3. Click **Save**

### 2. Configure Package Visibility (Optional)

By default, packages are private. To make them public:

1. After first build, go to: https://github.com/users/LukeEvansTech/packages
2. Click on your container package
3. Go to **Package settings**
4. Under **Danger Zone** → Change visibility to **Public**

## How the CI/CD Works

### Automatic Builds

The workflow triggers automatically when you:
- **Push to main** - Builds and pushes changed apps with `latest` tag
- **Open a PR** - Builds (but doesn't push) for testing
- **Push tags** - Creates versioned releases (e.g., `v1.0.0`)

### Change Detection

The workflow only builds apps that have changed:
```
apps/
├── supermicro-ipmi-cert/   # Changed → builds
├── brother-printer-cert/   # No changes → skips
└── apc-cert/               # No changes → skips
```

### Manual Builds

Trigger builds manually from GitHub Actions:

1. Go to: https://github.com/LukeEvansTech/containers/actions/workflows/build-and-push.yaml
2. Click **Run workflow**
3. Optionally specify which app to build (or leave empty for all)

## Using Built Containers

### In Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cert-deploy
spec:
  containers:
  - name: deploy
    image: ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
    # Or pin to digest for immutability:
    # image: ghcr.io/lukevanstech/supermicro-ipmi-cert:latest@sha256:abc123...
```

### In Docker

```bash
docker pull ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
docker run ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

### With Docker Compose

```yaml
services:
  cert-deploy:
    image: ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

## Local Development

### Authenticate Docker to GHCR

```bash
# Create a personal access token (classic) with `read:packages` scope
# https://github.com/settings/tokens

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u lukevanstech --password-stdin
```

### Build Locally

```bash
cd apps/supermicro-ipmi-cert
docker build -t ghcr.io/lukevanstech/supermicro-ipmi-cert:dev .
```

### Push Manually (if needed)

```bash
docker push ghcr.io/lukevanstech/supermicro-ipmi-cert:dev
```

## Image Tags

The workflow creates these tags automatically:

| Tag | When | Example |
|-----|------|---------|
| `latest` | Every push to main | `ghcr.io/lukevanstech/supermicro-ipmi-cert:latest` |
| `main-<sha>` | Every push to main | `ghcr.io/lukevanstech/supermicro-ipmi-cert:main-abc1234` |
| `pr-<number>` | Pull requests | `ghcr.io/lukevanstech/supermicro-ipmi-cert:pr-42` |
| Semver | Git tags | `ghcr.io/lukevanstech/supermicro-ipmi-cert:1.0.0` |

## Features

### Multi-Architecture Builds

Images are built for:
- ✅ `linux/amd64` (x86_64)
- ✅ `linux/arm64` (ARM64/Apple Silicon)

Docker automatically pulls the correct architecture for your platform.

### Build Caching

GitHub Actions caches layers between builds for faster CI/CD.

### Attestations

All images include:
- **Provenance attestations** - Verifiable build information
- **SBOM** - Software Bill of Materials

Verify attestations:
```bash
gh attestation verify oci://ghcr.io/lukevanstech/supermicro-ipmi-cert:latest
```

## Troubleshooting

### Build Failed: "Permission denied"

**Fix**: Enable write permissions in repo settings (see step 1 above)

### Can't Pull Image: "access denied"

**Fix 1**: Make package public (see step 2 above)

**Fix 2**: Authenticate with GitHub token:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u lukevanstech --password-stdin
```

### Build Skipped: "No changes detected"

This is normal! The workflow only builds apps that have changed files.

To force a build:
- Use manual workflow dispatch
- Modify a file in the app directory
- Push an empty commit: `git commit --allow-empty -m "Trigger build"`

## Advanced: Creating Releases

To create a versioned release:

```bash
# Tag the commit
git tag v1.0.0
git push origin v1.0.0
```

This creates:
- `ghcr.io/lukevanstech/supermicro-ipmi-cert:1.0.0`
- `ghcr.io/lukevanstech/supermicro-ipmi-cert:1.0`
- `ghcr.io/lukevanstech/supermicro-ipmi-cert:latest`

## Monitoring Builds

View build status:
- **Actions tab**: https://github.com/LukeEvansTech/containers/actions
- **Packages**: https://github.com/users/LukeEvansTech/packages

Each build shows:
- ✅ Build status
- 📦 Image digest
- 🏷️ Tags created
- 🔍 Attestations
