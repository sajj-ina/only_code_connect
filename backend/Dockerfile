# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Create a non-root user and group
RUN groupadd --system appuser && useradd --system --gid appuser appuser

# Combine apt update and install in a single RUN command to keep the image small
# The `procps` package provides the `top` command
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies as the root user.
# This is necessary as some packages might require elevated privileges for installation.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code and set ownership.
# This ensures the appuser has correct permissions for the application files.
COPY --chown=appuser:appuser ./app /app

# Switch to the non-root user for subsequent instructions.
# This ensures the application runs with the correct user.
USER appuser

# The command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
