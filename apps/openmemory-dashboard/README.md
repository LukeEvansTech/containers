# OpenMemory Dashboard

Web UI for OpenMemory - A long-term memory engine for AI applications.

## Description

This container provides the web dashboard interface for OpenMemory, allowing you to:
- Browse memories per sector
- See decay curves
- Explore graph links
- Visualize timelines
- Chat with memory

## Image Information

- **Base Image**: `node:20-alpine`
- **Upstream Source**: [CaviraOSS/OpenMemory](https://github.com/CaviraOSS/OpenMemory)
- **License**: Apache-2.0
- **Port**: 3000

## Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | URL to OpenMemory backend API | Yes | `https://openmemory.codelooks.com` |
| `NEXT_PUBLIC_API_KEY` | API key for backend authentication | Yes (if backend has auth enabled) | `your-api-key-here` |
| `NODE_ENV` | Node environment | No | `production` (default) |
| `PORT` | Port to listen on | No | `3000` (default) |
| `HOSTNAME` | Hostname to bind to | No | `0.0.0.0` (default) |

## Usage

### Docker Run

```bash
docker run -d \
  --name openmemory-dashboard \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://openmemory.codelooks.com \
  -e NEXT_PUBLIC_API_KEY=your-api-key-here \
  ghcr.io/lukeevanstech/openmemory-dashboard:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  openmemory-dashboard:
    image: ghcr.io/lukeevanstech/openmemory-dashboard:latest
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: https://openmemory.codelooks.com
      NEXT_PUBLIC_API_KEY: your-api-key-here
    restart: unless-stopped
```

## Health Check

The container includes a built-in health check that polls `http://localhost:3000` every 30 seconds.

## Building

```bash
docker build \
  --build-arg OPENMEMORY_VERSION=1.2.1 \
  -t ghcr.io/lukeevanstech/openmemory-dashboard:1.2.1 \
  .
```

## Links

- [Upstream Repository](https://github.com/CaviraOSS/OpenMemory)
- [Dashboard Documentation](https://github.com/CaviraOSS/OpenMemory/tree/main/dashboard)
- [OpenMemory Documentation](https://openmemory.cavira.app/docs)
