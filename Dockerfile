# Multi-stage Docker build for AI Load Consolidation Platform

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p processed_data reports optimization/results forecasting/results uploads

# Expose ports
EXPOSE 8000 8501

# Default command (can be overridden)
CMD ["python", "run_all_modules.py"]
