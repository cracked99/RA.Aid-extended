# Docker Environment for RA.Aid

This repository contains a patch file that adds Docker/Podman support to the RA.Aid project.

## What's Included

The patch adds the following files:

- `Dockerfile` - For production builds
- `Dockerfile.dev` - For development environment
- `Dockerfile.frontend` - For frontend development
- `docker-compose.yml` - For orchestrating the services
- `.dockerignore` - To exclude unnecessary files
- `.env.example` - Template for environment variables
- `README.docker.md` - Documentation for using Docker with RA.Aid

## How to Apply the Patch

1. Clone the RA.Aid repository:
   ```bash
   git clone https://github.com/ai-christianson/RA.Aid.git
   cd RA.Aid
   ```

2. Create a new branch:
   ```bash
   git checkout -b ra-aid-extended
   ```

3. Download the patch file from this repository.

4. Apply the patch:
   ```bash
   git apply docker-environment.patch
   ```

5. Commit the changes:
   ```bash
   git add .
   git commit -m "Add Docker development environment"
   ```

6. Push to your fork (if you have one):
   ```bash
   git push -u origin ra-aid-extended
   ```

## Using the Docker Environment

Once you've applied the patch, follow the instructions in `README.docker.md` to use the Docker environment.

## Creating a Pull Request

If you want to contribute these changes back to the main repository:

1. Fork the RA.Aid repository on GitHub
2. Apply the patch to your fork
3. Create a pull request from your `ra-aid-extended` branch to the main repository's `master` branch
