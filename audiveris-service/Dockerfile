FROM eclipse-temurin:17-jdk-jammy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Audiveris 5.3.1 from vendored archive in repo (tools/audiveris-5.3.1.zip)
ENV AUDIVERIS_VERSION=5.3.1
ENV AUDIVERIS_HOME=/opt/Audiveris
COPY tools/audiveris-5.3.1.zip /tmp/audiveris.zip
RUN unzip /tmp/audiveris.zip -d /opt \
    && mv /opt/audiveris-${AUDIVERIS_VERSION} ${AUDIVERIS_HOME} \
    && rm /tmp/audiveris.zip

ENV AUDIVERIS_PATH=${AUDIVERIS_HOME}/bin/Audiveris

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create directories used by the service
RUN mkdir -p /tmp/uploads /tmp/output

# Expose Cloud Run port
ENV PORT=8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Explicit entrypoint to avoid base image defaults
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
