FROM eclipse-temurin:17-jdk-jammy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Build and install Audiveris 5.3.1 from source archive
ENV AUDIVERIS_VERSION=5.3.1
ENV AUDIVERIS_HOME=/opt/Audiveris
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && curl -L "https://github.com/Audiveris/audiveris/archive/refs/tags/${AUDIVERIS_VERSION}.zip" -o /tmp/audiveris-src.zip \
    && unzip /tmp/audiveris-src.zip -d /tmp \
    && mv /tmp/audiveris-${AUDIVERIS_VERSION} /tmp/audiveris \
    && rm /tmp/audiveris-src.zip \
    && cd /tmp/audiveris \
    && test -f build.gradle || (echo \"build.gradle not found after extracting archive\" && ls -la && exit 1) \
    && git init \
    && git config user.email \"builder@localhost\" \
    && git config user.name \"Docker Builder\" \
    && git add . \
    && git commit -m \"build\" >/dev/null \
    && chmod +x gradlew \
    && ./gradlew --no-daemon -x test -x git_build -PprogramBuild=docker assembleDist \
    && DIST_ZIP=$(find build/distributions -maxdepth 1 -name \"audiveris-*.zip\" -print -quit) \
    && [ -n \"$DIST_ZIP\" ] \
    && unzip \"$DIST_ZIP\" -d /opt \
    && AUDIVERIS_EXTRACTED=$(find /opt -maxdepth 1 -type d -name \"audiveris*\" -print -quit) \
    && [ -n \"$AUDIVERIS_EXTRACTED\" ] \
    && mv \"$AUDIVERIS_EXTRACTED\" \"${AUDIVERIS_HOME}\" \
    && rm -rf /tmp/audiveris

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
