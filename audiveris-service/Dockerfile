FROM eclipse-temurin:17-jdk-jammy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    unzip \
    git \
    maven \
    && rm -rf /var/lib/apt/lists/*

# Build and install Audiveris 5.3.1 from source archive
ENV AUDIVERIS_VERSION=5.3.1
ENV AUDIVERIS_HOME=/opt/Audiveris

# Download and extract source
RUN curl -L "https://github.com/Audiveris/audiveris/archive/refs/tags/${AUDIVERIS_VERSION}.zip" -o /tmp/audiveris-src.zip \
    && unzip /tmp/audiveris-src.zip -d /tmp \
    && mv /tmp/audiveris-${AUDIVERIS_VERSION} /tmp/audiveris \
    && rm /tmp/audiveris-src.zip

# Verify build.gradle exists
RUN cd /tmp/audiveris && test -f build.gradle || (echo "ERROR: build.gradle not found" && ls -la && exit 1)

# Install JAI dependency that's missing from public repos
RUN curl -L "https://repo.osgeo.org/repository/release/javax/media/jai-core/1.1.3/jai-core-1.1.3.jar" -o /tmp/jai-core-1.1.3.jar \
    && mvn install:install-file \
        -DgroupId=javax.media.jai \
        -DartifactId=com.springsource.javax.media.jai.core \
        -Dversion=1.1.3 \
        -Dpackaging=jar \
        -Dfile=/tmp/jai-core-1.1.3.jar

# Build Audiveris distribution
RUN cd /tmp/audiveris \
    && chmod +x gradlew \
    && ./gradlew --no-daemon -x test -x git_build -PprogramBuild=docker assembleDist

# Extract and install the built distribution
RUN cd /tmp/audiveris \
    && ls -la build/distributions/ \
    && DIST_ZIP=$(find build/distributions -maxdepth 1 -name "audiveris-*.zip" | head -n 1) \
    && echo "Found distribution: $DIST_ZIP" \
    && if [ -z "$DIST_ZIP" ]; then echo "ERROR: No distribution zip found"; exit 1; fi \
    && unzip "$DIST_ZIP" -d /opt \
    && ls -la /opt/ \
    && AUDIVERIS_DIR=$(find /opt -maxdepth 1 -type d -name "audiveris*" -o -name "Audiveris*" | head -n 1) \
    && echo "Found extracted dir: $AUDIVERIS_DIR" \
    && if [ -z "$AUDIVERIS_DIR" ]; then echo "ERROR: No audiveris directory found in /opt"; exit 1; fi \
    && mv "$AUDIVERIS_DIR" "${AUDIVERIS_HOME}" \
    && ls -la "${AUDIVERIS_HOME}/bin/" \
    && rm -rf /tmp/audiveris /tmp/jai-core-1.1.3.jar

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
