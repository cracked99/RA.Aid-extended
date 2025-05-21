# Docker/Podman Development Environment for RA.Aid

This guide explains how to use Docker or Podman to set up a development environment for RA.Aid.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) or [Podman](https://podman.io/getting-started/installation)
- [Docker Compose](https://docs.docker.com/compose/install/) or [Podman Compose](https://github.com/containers/podman-compose)

## Environment Setup

1. Create a `.env` file in the project root with your API keys:

```
# Required for the default Anthropic provider
ANTHROPIC_API_KEY=your_api_key_here

# Optional: For OpenAI provider
# OPENAI_API_KEY=your_api_key_here

# Optional: For other providers
# OPENROUTER_API_KEY=your_api_key_here
# DEEPSEEK_API_KEY=your_api_key_here
# GEMINI_API_KEY=your_api_key_here
```

## Running the Development Environment

### Option 1: Full Stack (Backend + Frontend)

This will start both the RA.Aid server and a development frontend server:

```bash
# If using Docker
docker-compose up

# If using Podman
podman-compose up
```

- RA.Aid server will be available at: http://localhost:1818
- Frontend development server will be available at: http://localhost:5173

### Option 2: Backend Only

If you only want to run the RA.Aid server:

```bash
# If using Docker
docker-compose up ra-aid

# If using Podman
podman-compose up ra-aid
```

The server will be available at: http://localhost:1818

### Option 3: Frontend Development Only

If you already have the backend running locally and just want the frontend development environment:

```bash
# If using Docker
docker-compose up frontend

# If using Podman
podman-compose up frontend
```

The frontend will be available at: http://localhost:5173

## Development Workflow

The container setup mounts your local directory into the container, so any changes you make to the code will be reflected in the running application.

### Creating Fresh Projects

The Docker setup includes a dedicated workspace volume that allows you to create fresh projects without detecting existing files. When you access the RA.Aid web interface, you'll be able to create a new project from scratch.

To reset the workspace and start with a completely fresh project:

```bash
# Run the reset script
./reset-workspace.sh

# Or manually:
# If using Docker
docker-compose down
docker volume rm ra-aid-workspace-default
docker-compose up -d

# If using Podman
podman-compose down
podman volume rm ra-aid-workspace-default
podman-compose up -d
```

This will give you a clean workspace where you can create a new project from scratch.

### Python Code Changes

For Python code changes, you may need to restart the server:

```bash
# If using Docker
docker-compose restart ra-aid

# If using Podman
podman-compose restart ra-aid
```

### Frontend Code Changes

Frontend code changes should be automatically detected and hot-reloaded by the development server.

## Building for Production

To build a production-ready image:

```bash
# If using Docker
docker build -t ra-aid:latest .

# If using Podman
podman build -t ra-aid:latest .
```

Run the production image:

```bash
# If using Docker
docker run -p 1818:1818 --env-file .env ra-aid:latest

# If using Podman
podman run -p 1818:1818 --env-file .env ra-aid:latest
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Fix ownership issues
sudo chown -R $(id -u):$(id -g) .

# For SELinux systems (when using Podman)
# The :Z volume mount option should handle this automatically,
# but if you still have issues:
sudo chcon -Rt container_file_t .
```

### Node.js Errors

If you encounter Node.js related errors:

```bash
# Enter the container (Docker)
docker-compose exec ra-aid bash

# Enter the container (Podman)
podman exec -it $(podman ps -q -f name=ra-aid) bash

# Navigate to frontend directory and reinstall dependencies
cd frontend
npm install
npm run build:prebuilt
```

### Database Issues

The SQLite database is stored in the `.ra-aid` directory. If you need to reset it:

```bash
# Stop the containers (Docker)
docker-compose down
# OR (Podman)
podman-compose down

# Remove the database directory
rm -rf .ra-aid

# Start the containers again (Docker)
docker-compose up
# OR (Podman)
podman-compose up
```
