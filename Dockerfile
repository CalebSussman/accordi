# Akkordio Backend - Dockerfile
# Supports both OEMER and Audiveris for OMR processing

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install Python dependencies including OEMER
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir oemer

# Copy backend code
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads processed

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
