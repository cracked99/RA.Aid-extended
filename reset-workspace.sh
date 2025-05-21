#!/bin/bash

# Stop the containers
echo "Stopping containers..."
podman-compose down

# Remove the workspace volume
echo "Removing workspace volume..."
podman volume rm ra-aid-workspace-default

# Start the containers again
echo "Starting containers with fresh workspace..."
podman-compose up -d

echo "Done! You now have a fresh workspace."
echo "Access the application at:"
echo "  - Backend: http://localhost:1818"
echo "  - Frontend: http://localhost:5173"
