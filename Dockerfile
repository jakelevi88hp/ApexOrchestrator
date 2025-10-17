# Production Dockerfile for Apex Orchestrator
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src:$PYTHONPATH

# Create app user (security best practice)
RUN useradd -m -u 1000 -s /bin/bash apexuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=apexuser:apexuser . .

# Create necessary directories
RUN mkdir -p logs /app/work /app/backups /app/proposals && \
    chown -R apexuser:apexuser logs /app/work /app/backups /app/proposals

# Switch to non-root user
USER apexuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:APP", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

