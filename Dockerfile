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
# CACHE BUST: 2025-12-10-v3 - Force rebuild to verify installation
WORKDIR /tmp
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.8.1/Audiveris-5.8.1-ubuntu22.04-x86_64.deb && \
    dpkg -i Audiveris-5.8.1-ubuntu22.04-x86_64.deb || apt-get install -f -y && \
    rm Audiveris-5.8.1-ubuntu22.04-x86_64.deb

# CRITICAL: Verify what dpkg actually installed
RUN echo "=== Listing ALL files installed by audiveris package ===" && \
    dpkg -L audiveris && \
    echo "=== Searching filesystem for Audiveris ===" && \
    find / -name "*udiveris*" -o -name "*Audiveris*" 2>/dev/null | head -20 && \
    echo "=== Checking if /opt exists ===" && \
    ls -la /opt/ || echo "/opt does not exist" && \
    echo "=== End of Audiveris verification ==="

# Try to determine actual installation path
RUN AUDIVERIS_BIN=$(find /opt -name "Audiveris" -o -name "audiveris" 2>/dev/null | head -1) && \
    if [ -n "$AUDIVERIS_BIN" ]; then \
        echo "Found Audiveris at: $AUDIVERIS_BIN"; \
        AUDIVERIS_DIR=$(dirname "$AUDIVERIS_BIN"); \
        echo "Audiveris directory: $AUDIVERIS_DIR"; \
        export PATH="$AUDIVERIS_DIR:$PATH"; \
    else \
        echo "ERROR: Could not find Audiveris binary!"; \
        exit 1; \
    fi

# Set AUDIVERIS_PATH based on what we found
# Check multiple possible locations
ENV AUDIVERIS_PATH="/opt/Audiveris/bin/Audiveris"
RUN if [ -f "/opt/Audiveris/bin/Audiveris" ]; then \
        echo "Found at: /opt/Audiveris/bin/Audiveris"; \
    elif [ -f "/opt/Audiveris/bin/audiveris" ]; then \
        echo "Found at: /opt/Audiveris/bin/audiveris"; \
        export AUDIVERIS_PATH="/opt/Audiveris/bin/audiveris"; \
    elif [ -f "/usr/local/bin/Audiveris" ]; then \
        echo "Found at: /usr/local/bin/Audiveris"; \
        export AUDIVERIS_PATH="/usr/local/bin/Audiveris"; \
    else \
        echo "ERROR: Cannot locate Audiveris binary"; \
        exit 1; \
    fi

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
