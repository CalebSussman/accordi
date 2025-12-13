# Audiveris on Google Cloud Run - Deployment Plan

## Goal
Deploy Audiveris as a standalone microservice on Google Cloud Run to handle OMR processing for clean PDFs, while the main backend on Render uses OEMER for photos/scans.

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (GitHub Pages) │
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│   Main Backend  │    │  Audiveris API  │
│   (Render.com)  │───▶│ (Cloud Run)     │
│   + OEMER       │    │                 │
└─────────────────┘    └─────────────────┘
```

**Flow:**
1. User uploads PDF to main backend
2. If engine=audiveris, backend forwards to Cloud Run
3. Cloud Run processes PDF with Audiveris, returns MusicXML
4. Main backend returns result to frontend

## Implementation Steps

### Phase 1: Create Audiveris Microservice

#### 1.1 Create Project Structure
```
audiveris-service/
├── Dockerfile
├── main.py              # FastAPI wrapper
├── requirements.txt
├── .gcloudignore
└── README.md
```

#### 1.2 Dockerfile (audiveris-service/Dockerfile)
```dockerfile
# Use Audiveris base image
FROM jbarthelemy/audiveris:latest

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create directories
RUN mkdir -p /tmp/uploads /tmp/output

# Expose Cloud Run port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 1.3 Requirements (audiveris-service/requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
aiofiles==23.2.1
```

#### 1.4 FastAPI Application (audiveris-service/main.py)
```python
"""
Audiveris Microservice - Cloud Run
Provides OMR processing using Audiveris via REST API
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import subprocess
import asyncio
import aiofiles
import os
import uuid
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audiveris OMR API",
    description="Optical Music Recognition using Audiveris",
    version="1.0.0"
)

UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

AUDIVERIS_PATH = "/opt/Audiveris/bin/Audiveris"


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "audiveris-omr",
        "audiveris_available": os.path.exists(AUDIVERIS_PATH)
    }


@app.post("/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Process PDF with Audiveris and return MusicXML.

    Args:
        file: PDF file upload

    Returns:
        MusicXML file (.mxl)
    """
    # Validate PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
    async with aiofiles.open(pdf_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"Processing PDF: {job_id}")

    try:
        # Run Audiveris
        output_path = OUTPUT_DIR / job_id
        output_path.mkdir(exist_ok=True)

        process = await asyncio.create_subprocess_exec(
            AUDIVERIS_PATH,
            "-batch",
            "-export",
            "-output", str(output_path),
            str(pdf_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for completion (5 minute timeout)
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=300
        )

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8')
            logger.error(f"Audiveris failed: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Audiveris processing failed: {error_msg}"
            )

        # Find output MusicXML file
        musicxml_path = output_path / f"{pdf_path.stem}.mxl"
        if not musicxml_path.exists():
            # Try alternative extension
            musicxml_path = output_path / f"{pdf_path.stem}.musicxml"

        if not musicxml_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Audiveris completed but no output file found"
            )

        logger.info(f"Processing complete: {job_id}")

        # Return MusicXML file
        return FileResponse(
            musicxml_path,
            media_type="application/vnd.recordare.musicxml+xml",
            filename=f"{pdf_path.stem}.mxl"
        )

    except asyncio.TimeoutError:
        logger.error(f"Processing timeout: {job_id}")
        raise HTTPException(
            status_code=504,
            detail="Processing timed out after 5 minutes"
        )
    finally:
        # Cleanup
        if pdf_path.exists():
            pdf_path.unlink()


@app.get("/")
async def root():
    """API information"""
    return {
        "service": "Audiveris OMR API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Process PDF to MusicXML",
            "GET /health": "Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Phase 2: Deploy to Google Cloud Run

#### 2.1 Prerequisites
- Google Cloud account (free tier available)
- gcloud CLI installed: https://cloud.google.com/sdk/docs/install

#### 2.2 Setup Commands
```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Create new project (or use existing)
gcloud projects create akkordio-audiveris --name="Akkordio Audiveris"

# 3. Set project
gcloud config set project akkordio-audiveris

# 4. Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# 5. Navigate to service directory
cd audiveris-service/

# 6. Deploy to Cloud Run
gcloud run deploy audiveris-omr \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 3 \
  --min-instances 0

# 7. Get service URL
gcloud run services describe audiveris-omr \
  --region us-central1 \
  --format 'value(status.url)'
```

#### 2.3 Expected Output
```
Service URL: https://audiveris-omr-XXXXX-uc.a.run.app
```

### Phase 3: Update Main Backend

#### 3.1 Add Environment Variable
```bash
# On Render.com dashboard, add environment variable:
AUDIVERIS_API_URL=https://audiveris-omr-XXXXX-uc.a.run.app
```

#### 3.2 Update backend/omr.py
```python
# In _process_with_audiveris() method, replace Docker logic with HTTP call

async def _process_with_audiveris(
    self,
    pdf_path: Path,
    output_dir: Path,
    timeout: int
) -> Tuple[Path, dict]:
    """
    Process PDF with Audiveris via Cloud Run API.
    """
    import aiohttp

    audiveris_url = os.getenv('AUDIVERIS_API_URL')
    if not audiveris_url:
        raise OMRError("AUDIVERIS_API_URL not configured")

    try:
        musicxml_path = output_dir / f"{pdf_path.stem}.mxl"

        logger.info(f"Calling Audiveris Cloud Run API: {audiveris_url}")

        async with aiohttp.ClientSession() as session:
            # Upload PDF to Cloud Run
            with open(pdf_path, 'rb') as f:
                form = aiohttp.FormData()
                form.add_field('file', f, filename=pdf_path.name)

                async with session.post(
                    f"{audiveris_url}/process",
                    data=form,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status != 200:
                        error = await resp.text()
                        raise OMRError(f"Audiveris API failed: {error}")

                    # Save MusicXML response
                    async with aiofiles.open(musicxml_path, 'wb') as out:
                        await out.write(await resp.read())

        logger.info(f"Audiveris processing completed: {musicxml_path}")

        metadata = {
            "engine": "audiveris",
            "success": True,
            "warnings": [],
            "errors": []
        }

        return musicxml_path, metadata

    except asyncio.TimeoutError:
        logger.error(f"Audiveris API timeout after {timeout} seconds")
        raise OMRError("Audiveris processing timed out")
    except Exception as e:
        logger.error(f"Audiveris API error: {e}")
        raise OMRError(f"Audiveris processing failed: {str(e)}")
```

#### 3.3 Update requirements.txt
```bash
# Add to backend/requirements.txt
aiohttp==3.9.1
```

### Phase 4: Testing

#### 4.1 Test Audiveris Service Directly
```bash
# Test health endpoint
curl https://audiveris-omr-XXXXX-uc.a.run.app/health

# Test with sample PDF
curl -X POST \
  -F "file=@sample_score.pdf" \
  https://audiveris-omr-XXXXX-uc.a.run.app/process \
  -o output.mxl
```

#### 4.2 Test from Main Backend
```bash
# Upload PDF via Akkordio frontend
# Select "Audiveris" engine
# Verify processing succeeds
```

### Phase 5: Monitoring & Cost Management

#### 5.1 Cloud Run Free Tier
- 2 million requests/month
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds
- Free egress: 1 GB/month

**Expected cost for Akkordio:**
- Typical usage: ~100 requests/day
- Mostly within free tier
- Estimated cost: $0-5/month

#### 5.2 Monitoring
```bash
# View logs
gcloud run services logs read audiveris-omr --region us-central1

# View metrics in Cloud Console
# https://console.cloud.google.com/run
```

#### 5.3 Cost Optimization
```yaml
# Set in deployment:
min-instances: 0          # Scale to zero when idle
max-instances: 3          # Limit concurrent instances
cpu: 2                    # Sufficient for Audiveris
memory: 2Gi               # Required for Java/Audiveris
timeout: 600              # 10 minute max
```

## Deployment Checklist

- [ ] Create audiveris-service/ directory structure
- [ ] Write Dockerfile with Audiveris base image
- [ ] Write FastAPI application (main.py)
- [ ] Write requirements.txt
- [ ] Install gcloud CLI
- [ ] Create Google Cloud project
- [ ] Enable Cloud Build and Cloud Run APIs
- [ ] Deploy to Cloud Run
- [ ] Get service URL
- [ ] Add AUDIVERIS_API_URL to Render environment
- [ ] Update backend/omr.py with HTTP client
- [ ] Add aiohttp to backend requirements
- [ ] Test Audiveris service directly
- [ ] Test end-to-end from frontend
- [ ] Monitor logs and performance
- [ ] Document service URL in README

## Rollback Plan

If deployment fails or costs exceed budget:

1. **Remove from backend:**
   - Remove AUDIVERIS_API_URL environment variable
   - Backend will fall back to "engine not available" error

2. **Delete Cloud Run service:**
   ```bash
   gcloud run services delete audiveris-omr --region us-central1
   ```

3. **Users can still use OEMER:**
   - Default engine remains OEMER
   - No impact on core functionality

## Future Enhancements

1. **Authentication:** Add API key to Cloud Run service
2. **Caching:** Cache processed PDFs to reduce costs
3. **Batch Processing:** Process multiple pages in parallel
4. **Custom Domain:** Map custom domain to Cloud Run URL
5. **CDN:** Use Cloud CDN for static MusicXML serving

## Security Considerations

1. **Public Access:** Service is public (allow-unauthenticated)
   - Safe: Only processes PDFs, no sensitive data
   - Alternative: Add API key authentication

2. **File Cleanup:** Temporary files cleaned up after processing
   - Prevents disk space issues
   - No data persistence

3. **Rate Limiting:** Cloud Run has built-in DDoS protection
   - 1000 requests/second limit per service
   - Sufficient for Akkordio usage

---

**Created:** 2025-12-12
**Status:** Planning - Ready for Implementation
**Priority:** Medium - Alternative to Docker-in-Docker on Render
