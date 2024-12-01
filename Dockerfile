# Use a specific, slim Python image
FROM python:3.11.4-slim

# Set environment variables for optimal performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# Install system dependencies and clean up afterward
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

# Change ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser
