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
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.8.1/Audiveris-5.8.1-ubuntu22.04-x86_64.deb && \
    dpkg -i Audiveris-5.8.1-ubuntu22.04-x86_64.deb || apt-get install -f -y && \
    rm Audiveris-5.8.1-ubuntu22.04-x86_64.deb

# Find where Audiveris was installed and verify it works
RUN echo "=== Finding Audiveris installation ===" && \
    find / -name "Audiveris" -o -name "audiveris" 2>/dev/null | head -10 && \
    echo "=== Checking dpkg contents ===" && \
    dpkg -L audiveris 2>/dev/null | grep -i bin || true

# Add Audiveris to PATH based on where it was installed
# The .deb package installs to /opt/Audiveris/bin
ENV PATH="/opt/Audiveris/bin:${PATH}"

# Don't set AUDIVERIS_PATH - let it default to searching PATH
# This avoids conflicts with Render environment variables

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
