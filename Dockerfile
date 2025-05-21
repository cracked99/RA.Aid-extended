FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    ripgrep \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy the entire application first
COPY . .

# Install the package in development mode
RUN pip install -e ".[dev]"

# Build frontend assets
WORKDIR /app/frontend
RUN npm install
RUN npm run build:prebuilt

# Return to app directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 1818

# Command to run the application
CMD ["ra-aid", "--server", "--server-port", "1818", "--server-host", "0.0.0.0"]
