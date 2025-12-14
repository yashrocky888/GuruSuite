# Phase 21: Dockerfile for Guru API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port (Cloud Run uses 8080)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEPLOYMENT_ENV=production

# Run the application (Cloud Run compatible - uses PORT env var)
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}
