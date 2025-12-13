# Audiveris Cloud Run Deployment Guide

## Overview

This guide walks you through deploying the Audiveris OMR microservice to Google Cloud Run to solve the memory limitation issue on Render's free tier.

**Why this is needed:**
- OEMER requires ~2GB+ RAM for deep learning models
- Render free tier only has 512 MB RAM
- Google Cloud Run free tier provides 2 GB memory instances
- Keeps your entire stack free!

## Prerequisites

1. **Google Cloud Account**
   - Sign up at https://cloud.google.com
   - Free tier includes:
     - 2 million requests/month
     - 360,000 GB-seconds of memory
     - 180,000 vCPU-seconds

2. **Install Google Cloud CLI**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

3. **Authenticate**
   ```bash
   gcloud auth login
   ```

## Step-by-Step Deployment

### 1. Create Google Cloud Project

```bash
# Create new project
gcloud projects create akkordio-audiveris --name="Akkordio Audiveris"

# Set as active project
gcloud config set project akkordio-audiveris

# Enable billing (required even for free tier)
# Go to: https://console.cloud.google.com/billing
# Link your project to billing account
```

### 2. Enable Required APIs

```bash
# Enable Cloud Build and Cloud Run
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 3. Deploy to Cloud Run

```bash
# Navigate to the audiveris-service directory
cd audiveris-service/

# Deploy (this will build and deploy in one command)
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

# Note: First build takes ~10-15 minutes (compiling Audiveris from source)
# Subsequent deployments are faster due to layer caching
```

**Deployment Options Explained:**
- `--source .` - Builds from current directory (uses Dockerfile)
- `--region us-central1` - Deploy to US Central region
- `--allow-unauthenticated` - Public access (no auth required)
- `--memory 2Gi` - 2 GB RAM (sufficient for Audiveris)
- `--cpu 2` - 2 vCPUs for faster processing
- `--timeout 600` - 10 minute timeout for large PDFs
- `--max-instances 3` - Limit concurrent instances (cost control)
- `--min-instances 0` - Scale to zero when idle (free!)

### 4. Get Service URL

After deployment completes, you'll see output like:
```
Service URL: https://audiveris-omr-XXXXX-uc.a.run.app
```

Save this URL! You'll need it for the next step.

Alternatively, retrieve it anytime with:
```bash
gcloud run services describe audiveris-omr \
  --region us-central1 \
  --format 'value(status.url)'
```

### 5. Test the Service

```bash
# Test health endpoint
curl https://audiveris-omr-XXXXX-uc.a.run.app/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "audiveris-omr",
#   "audiveris_available": true
# }

# Test with sample PDF (replace with your PDF)
curl -X POST \
  -F "file=@sample_score.pdf" \
  https://audiveris-omr-XXXXX-uc.a.run.app/process \
  -o output.mxl
```

### 6. Configure Render Backend

Add the Audiveris API URL as an environment variable on Render:

1. Go to https://dashboard.render.com
2. Select your **akkordio** service
3. Go to **Environment** tab
4. Add new environment variable:
   - **Key:** `AUDIVERIS_API_URL`
   - **Value:** `https://audiveris-omr-XXXXX-uc.a.run.app` (your Cloud Run URL)
5. Click **Save Changes**
6. Render will automatically redeploy with the new environment variable

### 7. Test End-to-End

1. Go to https://calebsussman.github.io/accordi/
2. Click **Settings** (gear icon)
3. Select **Audiveris** as OMR Engine
4. Upload a PDF
5. Watch the progress bar:
   - 📄 Uploading
   - 🎵 Converting to MusicXML (calls Cloud Run)
   - 🎹 Rendering Score

## Monitoring & Debugging

### View Logs

```bash
# View recent logs
gcloud run services logs read audiveris-omr --region us-central1

# Follow logs in real-time
gcloud run services logs tail audiveris-omr --region us-central1
```

### Check Metrics

```bash
# Open Cloud Run console
open https://console.cloud.google.com/run
```

View:
- Request count
- Response times
- Error rates
- Memory usage
- CPU usage

### Common Issues

**Issue: Build fails with "source repository not found"**
- Make sure you're in the `audiveris-service/` directory
- Check that `Dockerfile`, `main.py`, and `requirements.txt` exist

**Issue: Service times out (504)**
- Large PDFs may take longer than expected
- Check logs: `gcloud run services logs read audiveris-omr --region us-central1`
- Increase timeout: add `--timeout 900` (15 minutes) to deploy command

**Issue: "Permission denied" errors**
- Run: `gcloud auth login`
- Make sure you have Owner or Editor role on the project

**Issue: Service shows "Unhealthy"**
- Check logs for Audiveris compilation errors
- Verify Java 17 is available in container
- Test health endpoint manually: `curl YOUR_URL/health`

## Cost Management

### Free Tier Limits

Your usage should stay well within free tier:
- **Requests:** 2M/month (you'll use ~100-500/month)
- **Memory:** 360,000 GB-seconds (plenty for occasional processing)
- **CPU:** 180,000 vCPU-seconds (sufficient)
- **Bandwidth:** 1 GB/month out (MusicXML files are small)

**Estimated monthly cost: $0-2**

### Monitor Costs

```bash
# Check current month's usage
open https://console.cloud.google.com/billing
```

### Cost-Saving Tips

1. **Scale to zero:** With `--min-instances 0`, you only pay when processing
2. **Limit instances:** `--max-instances 3` prevents runaway costs
3. **Set billing alerts:** Get notified if costs exceed $5/month
4. **Regional deployment:** Use `us-central1` (cheaper than `us-west1`)

### Set Billing Alert

```bash
# Open billing alerts
open https://console.cloud.google.com/billing/alerts
```

Create alert:
- **Budget amount:** $5/month
- **Alert at:** 50%, 90%, 100%
- **Email:** your-email@example.com

## Updating the Service

When you make changes to the Audiveris service:

```bash
cd audiveris-service/

# Redeploy with same settings
gcloud run deploy audiveris-omr \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600

# Cloud Run will:
# 1. Build new image
# 2. Deploy with zero downtime
# 3. Route traffic to new version
```

## Rollback (If Needed)

If something breaks:

### Option 1: Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list --service audiveris-omr --region us-central1

# Rollback to specific revision
gcloud run services update-traffic audiveris-omr \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

### Option 2: Delete Service (Back to OEMER Only)

```bash
# Delete Cloud Run service
gcloud run services delete audiveris-omr --region us-central1

# Remove environment variable from Render
# Go to Render Dashboard → akkordio → Environment
# Delete AUDIVERIS_API_URL
```

Backend will automatically fall back to OEMER (though it will still have memory issues).

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (GitHub Pages) │ ← User uploads PDF, selects engine
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Main Backend   │
│  (Render.com)   │ ← Handles upload, job management
│  512 MB RAM     │
└────────┬────────┘
         │
         │ HTTP POST /process
         │ (only when engine=audiveris)
         ▼
┌─────────────────┐
│  Audiveris OMR  │
│ (Cloud Run)     │ ← PDF → MusicXML conversion
│  2 GB RAM       │   Returns .mxl file
└─────────────────┘
```

## Security Considerations

### Current Setup: Public Access

The service is deployed with `--allow-unauthenticated` for simplicity.

**Risks:**
- Anyone can call your service
- Potential for abuse (someone processing lots of PDFs)

**Mitigations:**
- Cloud Run has built-in rate limiting (1000 req/s)
- Max instances limit prevents runaway costs
- Can enable authentication later if needed

### Add Authentication (Optional)

If you want to restrict access:

```bash
# Redeploy with authentication required
gcloud run deploy audiveris-omr \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated

# Your backend will need to pass auth token
# See: https://cloud.google.com/run/docs/authenticating/service-to-service
```

## Troubleshooting

### Build Fails

**Symptom:** Deployment fails during build

**Solutions:**
1. Check Dockerfile syntax
2. Verify all files exist (`ls -la`)
3. Check build logs:
   ```bash
   gcloud builds list --limit=1
   gcloud builds log BUILD_ID
   ```

### Service Returns 500 Errors

**Symptom:** `/process` endpoint returns 500

**Solutions:**
1. Check if Audiveris binary exists:
   ```bash
   # Shell into running instance (while processing)
   gcloud run services proxy audiveris-omr --region us-central1
   ```
2. Verify PDF is valid
3. Check service logs for errors

### High Latency

**Symptom:** Processing takes very long

**Solutions:**
1. Increase CPU: `--cpu 4`
2. Check region latency (try `us-east1` if you're on east coast)
3. Review logs for bottlenecks

## Support

If you encounter issues:

1. **Check logs:** `gcloud run services logs read audiveris-omr --region us-central1`
2. **Check health:** `curl YOUR_URL/health`
3. **Google Cloud Status:** https://status.cloud.google.com
4. **Stack Overflow:** Tag questions with `google-cloud-run` and `audiveris`

## Summary

You've successfully:
- ✅ Created Google Cloud project
- ✅ Deployed Audiveris to Cloud Run
- ✅ Configured Render backend to use Cloud Run
- ✅ Set up monitoring and billing alerts
- ✅ Tested end-to-end PDF processing

**Result:** Free-tier OMR processing with 2 GB memory!

---

**Created:** 2025-12-13
**Status:** Ready for Deployment
**Estimated Setup Time:** 20-30 minutes
