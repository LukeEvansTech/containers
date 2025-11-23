# OpenMemory Container Image

This directory contains the Dockerfile for building OpenMemory container images.

## About OpenMemory

OpenMemory is an open-source cognitive memory engine that adds long-term memory to AI systems. It provides persistent memory with multi-sector cognitive structure, enabling AI systems to maintain context across conversations.

- **Upstream Repository**: https://github.com/CaviraOSS/OpenMemory
- **Documentation**: https://openmemory.cavira.app/

## Version Management

This container image **mirrors OpenMemory's versioning exactly**:
- The `VERSION` file in this directory tracks the current OpenMemory release
- Container images are tagged with OpenMemory's version numbers (e.g., `1.2.1`)
- The automated workflow checks daily for new OpenMemory releases and rebuilds automatically

**Current Version**: See [VERSION](./VERSION) file

## Image Details

- **Registry**: `ghcr.io/lukeevainstech/openmemory`
- **Port**: 8080
- **User**: Non-root (UID/GID 1001)
- **Data Directory**: `/app/data` (for SQLite database)
- **Health Check**: HTTP GET on `/health` endpoint

## Available Tags

- `latest` - Always points to the latest OpenMemory release
- `1.2.1`, `1.2.0`, etc. - Specific OpenMemory versions
- `1.2`, `1` - Major.minor and major version tags (follows semantic versioning)

## Building

The image is automatically built when changes are pushed to this directory or manually triggered via GitHub Actions workflow dispatch.

To build manually:

```bash
docker build -t ghcr.io/lukeevainstech/openmemory:latest .
```

To build a specific OpenMemory version:

```bash
docker build --build-arg OPENMEMORY_VERSION=v1.0.0 -t ghcr.io/lukeevainstech/openmemory:v1.0.0 .
```

## Running

Basic usage:

```bash
docker run -d \
  -p 8080:8080 \
  -v openmemory-data:/app/data \
  -e OM_API_KEY=your-secret-api-key \
  ghcr.io/lukeevainstech/openmemory:latest
```

## Environment Variables

See the [official documentation](https://openmemory.cavira.app/docs/installation) for a complete list of environment variables.

Key variables:
- `OM_API_KEY`: API key for authentication (required)
- `OM_PORT`: Server port (default: 8080)
- `OM_METADATA_BACKEND`: Backend type (sqlite/postgres)
- `OM_VECTOR_BACKEND`: Vector storage (sqlite/pgvector/weaviate)
- `OM_DB_PATH`: SQLite database path (default: ./data/openmemory.sqlite)
- `OM_EMBEDDINGS`: Embedding provider (openai/gemini/ollama/local)

## Automatic Builds

This image is automatically rebuilt when:
- Changes are made to files in this directory
- A new OpenMemory release is published (via scheduled workflow)
- Manually triggered via GitHub Actions

The `watch-upstream-releases` workflow checks for new OpenMemory releases daily and triggers a rebuild if a new version is detected.
