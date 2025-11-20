# Protégé in Lex Machina A2A Proxy

[![Release](https://img.shields.io/github/v/release/LexMachinaInc/lexmachina-agent)](https://img.shields.io/github/v/release/LexMachinaInc/lexmachina-agent)
[![Build status](https://img.shields.io/github/actions/workflow/status/LexMachinaInc/lexmachina-agent/main.yml?branch=main)](https://github.com/LexMachinaInc/lexmachina-agent/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/LexMachinaInc/lexmachina-agent)](https://img.shields.io/github/commit-activity/m/LexMachinaInc/lexmachina-agent)
[![License](https://img.shields.io/github/license/LexMachinaInc/lexmachina-agent)](https://img.shields.io/github/license/LexMachinaInc/lexmachina-agent)

A2A agent for Lex Machina



- **Github repository**: <https://github.com/LexMachinaInc/lexmachina-agent/>
- **Documentation** <https://LexMachinaInc.github.io/lexmachina-agent/>

## What is an A2A Proxy?

An [Agent-to-Agent (A2A)](https://a2a-protocol.org/latest/) proxy is a specialized service that acts as an intermediary between different AI agents, enabling them to communicate and collaborate effectively. It standardizes the communication protocol, allowing agents with different architectures and capabilities to understand each other.

Key functions of this A2A proxy include:
- **Standardized Interface**: It exposes a consistent API for other agents to interact with, abstracting away the complexities of the underlying Lex Machina services.
- **Request/Response Handling**: It receives requests from a primary agent, translates them into a format understood by the Lex Machina API, and returns the response in a standardized format.
- **Authentication and Authorization**: It manages credentials for the Lex Machina API, so the requesting agent doesn't need to handle them directly.
- **Data Transformation**: It can enrich or reformat data from the Lex Machina API to meet the needs of the requesting agent in a single request.

In essence, this proxy makes it easy to integrate Lex Machina's data and analytics capabilities into a larger ecosystem of AI agents without requiring each agent to have specific knowledge of the Lex Machina API.

## Environment Variables

The the application and container accepts the following environment variables:

- `BASE_URL`: URL where this application will be available (default: `http://localhost:10011`)
- `API_BASE_URL`: Base URL for the Lex Machina API (default: `https://law-api-poc.stage.lexmachina.com`)
- `CLIENT_ID`: OAuth2 client ID (requires CLIENT_SECRET)
- `CLIENT_SECRET`: OAuth2 client secret (requires CLIENT_ID)
- `DELEGATION_URL`: URL for OAuth2 delegation-based authentication (not yet implemented)
- `API_TOKEN`: Direct API token for authentication (not recommended)

OAuth2 client credentials can be managed using [Lex Machina API Settings](https://law.lexmachina.com/api-settings)


## Docker Compose Usage

```bash
just compose-up
```

Using either docker or nerdctl will start both lexmachina-agent and a copy of [a2a-inspector](https://github.com/a2aproject/a2a-inspector) for local testing.

## Docker Usage

### Pulling from GitHub Container Registry

Docker images are automatically published to GitHub Container Registry on every release and main branch push:

```bash
# Pull the latest stable release
docker pull ghcr.io/lexmachinainc/lexmachina-agent:latest

# Pull a specific version
docker pull ghcr.io/lexmachinainc/lexmachina-agent:0.0.2

# Pull the latest development version
docker pull ghcr.io/lexmachinainc/lexmachina-agent:main
```

### Running the Container

```bash
# Using OAuth2 client credentials
docker run -d \
  --name lexmachina-agent \
  -p 10011:10011 \
  -e CLIENT_ID=your_client_id \
  -e CLIENT_SECRET=your_client_secret \
  -e API_BASE_URL=https://law-api-poc.stage.lexmachina.com \
  ghcr.io/lexmachinainc/lexmachina-agent:latest

# Using environment file
docker run -d \
  --name lexmachina-agent \
  -p 10011:10011 \
  --env-file .env \
  ghcr.io/lexmachinainc/lexmachina-agent:latest
```


### Building Locally

```bash
# Build the image locally
docker build -t lexmachina-agent .

# Run your locally built image
docker run -p 10011:10011 lexmachina-agent
```

### Health Check

The agent runs on port 10011 and provides an A2A-compliant API. You can check if it's running by accessing the agent card:

```bash
curl http://localhost:10011/.well-known/agent-card.json
```
