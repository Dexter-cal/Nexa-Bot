# EPEX APEX v5.0 Production Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    nodejs \
    npm \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install EPEX in editable mode
RUN pip install -e .

# Expose ports for Web GUI and Instance Networking
EXPOSE 8000
EXPOSE 8001

# Create config volume
VOLUME /root/.epex

# Default command: Launch Command Center
ENTRYPOINT ["python", "epex.py"]
