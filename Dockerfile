# Akkordio Backend - Dockerfile
# Includes Python, Java, and Audiveris for OMR processing

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Download and install Audiveris
WORKDIR /tmp
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.6.0/Audiveris-5.6.0-linux-x86_64.deb && \
    dpkg -i Audiveris-5.6.0-linux-x86_64.deb || apt-get install -f -y && \
    rm Audiveris-5.6.0-linux-x86_64.deb

# Set Audiveris path
ENV AUDIVERIS_PATH=/opt/Audiveris/bin/Audiveris

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

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
