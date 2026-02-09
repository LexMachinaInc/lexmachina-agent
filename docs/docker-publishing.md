# Docker Publishing Workflow

This document explains how the Docker image publishing workflow works for the Lex Machina Agent.

## Overview

The project automatically builds and publishes Docker images to GitHub Container Registry (`ghcr.io`) using GitHub Actions. Images are published on:

- **Main branch pushes**: Development images tagged with `main` and SHA-based tags
- **Pull requests**: Builds images for testing (not published)
- **Git tags**: Release images with version tags and `latest` tag
- **Releases**: Stable images with full version tagging

## Workflows

### 1. Main Docker Workflow (`.github/workflows/docker-publish.yml`)

This workflow handles Docker image building and publishing for most scenarios:

- **Triggers**: Push to main, PR creation/updates, Git tag pushes
- **Platforms**: Multi-platform builds for `linux/amd64` and `linux/arm64`
- **Caching**: Uses GitHub Actions cache for faster builds
- **Attestation**: Generates build provenance attestations for security

#### Image Tags Generated:

- `main`: Latest development version from main branch
- `main-<sha>`: Specific commit from main branch
- `latest`: Latest stable release (only for main branch)
- `v1.2.3`: Specific version tags from Git tags
- `1.2`: Major.minor version
- `1`: Major version only

### 2. Release Workflow (`.github/workflows/on-release-main.yml`)

Enhanced release workflow that:

- Deploys documentation to GitHub Pages
- Publishes Docker images for releases
- Tags images as both `latest` and `stable`
- Uses same multi-platform build setup

## Image Repository

Published images are available at:
```
ghcr.io/lexmachinainc/lexmachina-agent
```

## Security Features

1. **Attestation**: Build provenance is attached to images
2. **OIDC Token**: Uses GitHub's OIDC for secure authentication
3. **Minimal Permissions**: Workflows use least-privilege access
4. **Multi-platform**: Supports both AMD64 and ARM64 architectures

## Image Metadata

All images include OCI-compliant labels:

- `org.opencontainers.image.title`: "Lex Machina Agent"
- `org.opencontainers.image.description`: "A2A agent for Lex Machina"
- `org.opencontainers.image.vendor`: "Lex Machina Inc."
- `org.opencontainers.image.licenses`: "Apache-2.0"
- `org.opencontainers.image.source`: Repository URL
- `org.opencontainers.image.created`: Build timestamp
- `org.opencontainers.image.version`: Version from Git
- `org.opencontainers.image.revision`: Git commit SHA

## Using Published Images

### Pull Latest Stable Release
```bash
docker pull ghcr.io/lexmachinainc/lexmachina-agent:latest
```

### Pull Development Version
```bash
docker pull ghcr.io/lexmachinainc/lexmachina-agent:main
```

### Pull Specific Version
```bash
docker pull ghcr.io/lexmachinainc/lexmachina-agent:v1.0.0
```

### Run with Environment Variables
```bash
docker run -d \
  --name lexmachina-agent \
  -p 10011:10011 \
  -e API_TOKEN=your_token \
  -e API_BASE_URL=https://law.lexmachina.com \
  ghcr.io/lexmachinainc/lexmachina-agent:latest
```

## Local Development

### Using Docker Compose
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API credentials

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Building Locally
```bash
# Build the image
docker build -t lexmachina-agent .

# Run locally built image
docker run -p 10011:10011 \
  -e API_TOKEN=your_token \
  lexmachina-agent
```

## Troubleshooting

### Image Not Found
Ensure you're using the correct registry and repository name:
```
ghcr.io/lexmachinainc/lexmachina-agent
```

### Authentication Issues
The images are public and don't require authentication to pull. If you encounter issues:

1. Check your network connectivity
2. Verify the tag exists: https://github.com/LexMachinaInc/lexmachina-agent/pkgs/container/lexmachina-agent
3. Try pulling without specifying a tag to get latest

### Build Failures
If the workflow fails:

1. Check the Actions tab for detailed error logs
2. Verify Dockerfile syntax
3. Ensure all dependencies in `uv.lock` are available
4. Check for network issues during dependency installation

## Maintenance

### Adding New Build Arguments
To add new build arguments:

1. Add `ARG` instructions to the Dockerfile
2. Add corresponding `build-args` to both workflows
3. Update the metadata extraction in workflows if needed

### Changing Image Tags
To modify tagging strategy:

1. Update the `tags:` section in the `docker/metadata-action` step
2. Refer to the [metadata action documentation](https://github.com/docker/metadata-action) for tag patterns

### Platform Support
To add or remove platforms:

1. Modify the `platforms:` field in the build step
2. Ensure base images support the target platforms
3. Test builds on all target platforms
