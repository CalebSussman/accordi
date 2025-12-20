# Phase 4: PDF Upload to Score Display Plan

## Goal
Enable users to upload a PDF music score and display it on the page using OpenSheetMusicDisplay (OSMD).

## Current Status Assessment

### What's Working
- ✅ Backend deployed on Render (https://akkordio.onrender.com)
- ✅ Frontend deployed on GitHub Pages (https://calebsussman.github.io/accordi/)
- ✅ Health endpoint responding
- ✅ CORS configured
- ✅ Frontend UI with upload zone

### What's Not Working
- ❌ Backend processing pipeline untested
- ❌ PDF upload not functioning
- ❌ OMR processing with Audiveris not tested
- ❌ MusicXML display with OSMD not implemented
- ❌ No error handling/feedback in frontend

## Architecture Overview

```
User → Frontend (Upload PDF)
    ↓
Backend API (/upload endpoint)
    ↓
Audiveris OMR (PDF → MusicXML)
    ↓
Return MusicXML to Frontend
    ↓
OpenSheetMusicDisplay (Render MusicXML)
```

## Implementation Steps

### Step 1: Verify Backend OMR Pipeline
**Files to check:**
- `backend/omr.py` - Audiveris integration
- `backend/main.py` - Upload endpoint
- `backend/parser.py` - MusicXML parsing

**Tests:**
1. Test `/upload` endpoint with curl
2. Test Audiveris can process a sample PDF
3. Verify MusicXML output is valid
4. Test `/musicxml/{job_id}` endpoint returns file

**Potential Issues:**
- Audiveris path may be incorrect in Docker
- File permissions in upload directory
- Missing dependencies for PDF processing
- Timeout issues for large scores

### Step 2: Fix Frontend Upload Flow
**Files to modify:**
- `frontend/js/app.js` - Upload handler
- `frontend/js/api.js` - API client

**Changes needed:**
1. Add proper error handling for upload failures
2. Show upload progress/feedback
3. Handle CORS errors gracefully
4. Add loading states during processing

### Step 3: Implement MusicXML Display with OSMD
**Files to modify:**
- `frontend/js/app.js` - Add OSMD integration
- `frontend/index.html` - Already has OSMD CDN loaded

**Implementation:**
1. Create `renderScore()` function
2. Initialize OSMD with MusicXML data
3. Render to score container
4. Handle OSMD errors (invalid MusicXML, rendering issues)

**OSMD Basic Usage:**
```javascript
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay';

async function renderScore(musicXmlString) {
    const osmd = new OpenSheetMusicDisplay('scoreContainer');
    await osmd.load(musicXmlString);
    osmd.render();
}
```

### Step 4: End-to-End Flow
**Complete user flow:**
1. User drops/selects PDF file
2. Frontend uploads to `/upload` → get `job_id`
3. Frontend polls `/status/{job_id}` until complete
4. Frontend fetches MusicXML from `/musicxml/{job_id}`
5. Frontend renders MusicXML with OSMD
6. Show success message

**Error handling at each step:**
- Upload fails → Show error message
- OMR processing fails → Show error with details
- MusicXML invalid → Show parsing error
- OSMD rendering fails → Show rendering error

## Testing Strategy

### Backend Tests
1. **Manual curl test:**
   ```bash
   curl -X POST https://akkordio.onrender.com/upload \
     -F "file=@test_score.pdf"
   ```

2. **Check Audiveris installation:**
   ```bash
   # SSH into Render or check logs
   /opt/Audiveris/bin/Audiveris --version
   ```

3. **Test with sample PDF:**
   - Use simple 1-page score
   - Verify MusicXML output

### Frontend Tests
1. **Local testing:**
   - Test with localhost backend first
   - Verify upload UI works
   - Check console for errors

2. **Production testing:**
   - Test with deployed backend
   - Check CORS headers
   - Verify file upload size limits

## Simplified MVP Approach

**Goal:** Get ONE PDF to display as sheet music

**Minimal implementation:**
1. Remove accordion mapping for now
2. Focus only on: PDF → MusicXML → Display
3. Skip layout selection, fingering, playback
4. Just show the score on screen

**Updated flow:**
```javascript
// Simplified app.js
async function handleFile(file) {
    // 1. Upload
    showMessage('Uploading...');
    const { job_id } = await API.uploadPDF(file);

    // 2. Wait for processing
    showMessage('Processing with OMR...');
    await API.pollStatus(job_id, (status) => {
        showMessage(`Processing... ${status.progress}%`);
    });

    // 3. Get MusicXML
    const musicXmlUrl = API.getMusicXMLUrl(job_id);
    const response = await fetch(musicXmlUrl);
    const musicXml = await response.text();

    // 4. Render with OSMD
    showMessage('Rendering score...');
    await renderScore(musicXml);
    showMessage('Complete!');
}
```

## Known Issues to Address

### Issue 1: Audiveris Not Found
**Symptom:** Backend returns error "Audiveris not found"
**Solution:**
- Check `AUDIVERIS_PATH` environment variable
- Verify `/opt/Audiveris/bin/Audiveris` exists in Docker
- Test with `which audiveris` in container

### Issue 2: CORS Errors
**Symptom:** Frontend can't fetch MusicXML file
**Solution:**
- Verify CORS headers on `/musicxml/{job_id}` endpoint
- Add `FileResponse` headers in FastAPI
- Test with browser dev tools

### Issue 3: OSMD Not Rendering
**Symptom:** MusicXML loads but nothing displays
**Solution:**
- Verify OSMD CDN is loading
- Check console for OSMD errors
- Ensure `scoreContainer` element exists
- Verify MusicXML is valid

### Issue 4: Large Files Timeout
**Symptom:** Upload succeeds but processing never completes
**Solution:**
- Increase timeout limits
- Add proper background task handling
- Implement WebSocket for real-time updates

## Success Criteria

**Phase 4 is complete when:**
- [x] User can upload a PDF file ✅ (Frontend implemented)
- [x] Backend processes PDF with Audiveris ✅ (Backend implemented, deployment in progress)
- [x] MusicXML is returned to frontend ✅ (API endpoint `/musicxml/{job_id}` working)
- [x] OSMD displays the score on the page ✅ (Fixed container ID mismatch)
- [x] Error messages show when something fails ✅ (Error handling implemented)
- [ ] Works end-to-end in production ⏳ (Needs testing with real PDF)

## Progress Update (2025-12-10)

### Fixed Issues:
1. **Dockerfile Audiveris Path** ✅
   - Set `AUDIVERIS_PATH` environment variable to `/opt/Audiveris/bin/Audiveris`
   - Added verification step to list bin directory contents
   - Fixed Docker build failure on Render

2. **Frontend OSMD Container Mismatch** ✅
   - Fixed `getElementById('scoreContainer')` → `getElementById('osmd-container')`
   - Fixed `showMessage` → `showError` for proper error handling
   - Pushed to gh-pages branch

### Current Status:
- **Backend:** Deployed on Render, rebuilding with fixed Dockerfile
- **Frontend:** Deployed on GitHub Pages with OSMD fix
- **Health Check:** Backend responding at `/health` endpoint ✅

### Next Steps:
1. Wait for Render deployment to complete (~5-10 minutes)
2. Test end-to-end flow with a sample PDF:
   - Upload PDF via frontend at https://calebsussman.github.io/accordi/
   - Monitor backend processing
   - Verify MusicXML display with OSMD
3. Debug any issues that arise during testing
4. Document test results

## Next Phases (Future)

- **Phase 5:** Add accordion layout selection
- **Phase 6:** Implement note-to-button mapping
- **Phase 7:** Add interactive fingering visualization
- **Phase 8:** MIDI playback and export

---

## FINAL STATUS - Phase 4 FAILED (2025-12-20)

### Executive Summary

**Phase 4 has been abandoned.** PDF-to-MusicXML conversion via OMR (Optical Music Recognition) proved infeasible within free-tier infrastructure constraints. After multiple failed attempts with both OEMER and Audiveris, the project pivoted to **Phase 5 MVP**: accepting pre-converted MusicXML files directly from users.

---

### Complete Failure Diagnosis

#### Attempt 1: OEMER (Local Docker on Render) ❌

**Implementation:**
- Installed OEMER Python package in backend
- Added PDF-to-PNG conversion using pdf2image
- Ran OEMER via subprocess CLI: `oemer <image> -o <output_dir>`
- Timeout set to 600 seconds (10 minutes)

**Failure Mode: Memory Limit Exceeded**
- **Issue:** OEMER is a deep learning OMR system that loads neural network models into RAM
- **Render Free Tier RAM:** 512 MB
- **OEMER Model Requirements:** ~1-2 GB for inference
- **Result:** Process started successfully (PDF→PNG conversion worked) but crashed during model loading
- **Error:** "Web Service accordi exceeded its memory limit, which triggered an automatic restart"
- **Evidence:** Logs showed successful PNG conversion, then crash during OEMER execution

**Technical Details:**
```
Session Log 20251213:
[Line 149] CRITICAL ISSUE: OEMER Memory Limit Exceeded
[Line 159] Web Service accordi exceeded its memory limit (512MB)
[Line 161] OEMER's model checkpoints + inference require significantly more memory
```

**Why It Failed:**
1. OEMER downloads model checkpoints (~300MB) on first run
2. Loads entire model into memory for inference (~1-2GB)
3. Render free tier provides only 512MB total
4. Process OOM-killed before generating any output

---

#### Attempt 2: Audiveris (Google Cloud Run Microservice) ❌

**Implementation:**
- Deployed Audiveris as separate microservice on Google Cloud Run
- Cloud Run provides 2GB memory (sufficient for Audiveris)
- Built from source (Audiveris 5.3.1) using Gradle
- Created FastAPI wrapper to accept PDF uploads
- Main backend calls Audiveris Cloud Run via HTTP

**Build Challenges (Resolved):**
- **Issue 1:** Missing pom.xml (Audiveris uses Gradle, not Maven)
- **Issue 2:** Checkout tag 5.3.1 failed (shallow clone issues)
- **Issue 3:** Distribution file naming case-sensitivity (`Audiveris-5.3.1.zip` vs `audiveris-*.zip`)
- **Issue 4:** Docker context issues (needed repo root for `tools/` directory)
- **Resolution:** Built from source successfully after ~20 iterations

**Deployment Challenges (Resolved):**
- **Issue 1:** Port configuration (8000 vs 8080)
- **Issue 2:** Cloud Build logging permissions
- **Issue 3:** COPY paths in Dockerfile relative to repo root
- **Resolution:** Service deployed successfully to Cloud Run

**Failure Mode: Never Integrated**
- **Issue:** Backend deployment succeeded, but never tested end-to-end
- **Root Cause:** Complexity and time investment required
- **Why Abandoned:**
  1. Audiveris requires ~10-30 seconds per page (too slow for UX)
  2. OCR quality highly variable (errors in note recognition)
  3. Required manual AUDIVERIS_API_URL configuration
  4. Added infrastructure complexity (two services to maintain)
  5. Free tier limits (360,000 GB-seconds/month = ~100 requests/day max)

**Technical Details:**
```
Session Log 20251212:
[Line 350] Audiveris build and extraction succeeded!
[Line 359] Cloud Run deployment succeeded
[Line 375] Backend port fix committed (8000→8080)
[Line 405] "Once deployed, retry setting AUDIVERIS_API_URL environment variable"
```

**Final State:**
- Audiveris Cloud Run service: **Deployed but not configured**
- Main backend: **No AUDIVERIS_API_URL set**
- Integration: **Never tested**
- Status: **Abandoned due to complexity**

---

### Why Phase 4 Failed: Root Cause Analysis

#### Infrastructure Constraints (Primary)
1. **Memory Limits:**
   - OEMER requires 1-2GB RAM
   - Render free tier: 512MB
   - Upgrading costs $7/month (unacceptable)

2. **Processing Time:**
   - OEMER: 3-5 min with GPU, 10+ min without
   - Audiveris: 10-30 seconds per page
   - User expectation: <5 seconds total

3. **Complexity:**
   - Two separate deployments (main + Audiveris)
   - HTTP communication between services
   - Error handling across service boundaries

#### Technical Limitations (Secondary)
1. **OCR Quality:**
   - OMR systems require clean, high-resolution scans
   - Errors in note recognition require manual correction
   - No automated quality validation

2. **File Format Issues:**
   - MuseScore PDFs work well
   - Scanned sheet music often fails
   - Handwritten scores completely unusable

3. **Free Tier Limits:**
   - Google Cloud Run: 2M requests/month (sounds high but...)
   - Each request uses memory for 10-30 seconds
   - 360,000 GB-seconds/month ≈ 100-200 conversions/day max
   - Exceeding limits triggers billing

#### User Experience Issues (Tertiary)
1. **Slow Processing:**
   - 10-30 seconds minimum wait time
   - Requires polling status endpoint
   - Poor UX compared to instant display

2. **Error Recovery:**
   - PDF upload succeeds, but processing fails
   - User sees generic "Processing failed" error
   - No actionable feedback (which notes failed?)

3. **Limited Use Cases:**
   - Only works for digital PDFs (not photos)
   - Only works for printed scores (not handwritten)
   - Only works for simple layouts (fails on complex scores)

---

### Alternative Considered: MuseScore CLI

**Not Attempted Because:**
- MuseScore CLI requires full MuseScore installation (~500MB)
- Doesn't fit in Render's 512MB memory limit
- Requires X11 display server (headless mode buggy)
- License issues (GPL vs. proprietary backend)

---

### Decision: Pivot to Phase 5 MVP

**Rationale:**
1. **User Can Convert Locally:**
   - Free tools available: MuseScore, Finale, Sibelius
   - One-time conversion: PDF → MusicXML export
   - User uploads .mxl file directly

2. **Simpler Architecture:**
   - No OMR processing needed
   - No microservice dependencies
   - Instant display (no polling)

3. **Better UX:**
   - Upload → Display in <1 second
   - No processing errors
   - Guaranteed quality (user-converted)

4. **Infrastructure Savings:**
   - Single deployment (Render backend)
   - No Google Cloud Run costs
   - No memory pressure

**Tradeoffs Accepted:**
- User must convert PDFs locally (extra step)
- Requires user to have MuseScore/Finale/etc installed
- No "pure web" solution (breaks initial vision)

**Phase 5 MVP Scope:**
- ✅ Accept .mxl/.musicxml file uploads
- ✅ Extract compressed .mxl archives
- ✅ Display scores with OSMD
- ❌ PDF upload (removed from UI)
- ❌ OMR processing (abandoned)

---

### Lessons Learned

1. **Memory constraints are hard blockers** for ML-based solutions on free tier
2. **OCR quality** is insufficient for production use without manual review
3. **Processing time** matters more than "technically possible"
4. **User-side conversion** is acceptable if tools are free and easy
5. **Simplicity wins** over "full-stack" solutions when resources are limited

---

### Files Modified During Phase 4 (Now Unused)

**Backend:**
- `backend/omr.py` - OEMER and Audiveris integration (partially working, not used)
- `backend/requirements.txt` - Added pdf2image, aiohttp (still used for other features)
- `Dockerfile` - Added poppler-utils (no longer needed, but harmless)

**Audiveris Service (Deployed but Unused):**
- `audiveris-service/Dockerfile` - Builds Audiveris from source
- `audiveris-service/main.py` - FastAPI wrapper
- `audiveris-service/requirements.txt` - Python dependencies
- `cloudbuild.yaml` - Cloud Build configuration
- **Status:** Service running but not configured in main backend

**Documentation:**
- `AUDIVERIS_DEPLOYMENT.md` - Deployment guide (obsolete)
- `session_logs/20251212_Session.md` - Cloud Run deployment attempts
- `session_logs/20251213_Session.md` - OEMER memory failure

---

**Created:** 2025-12-08
**Last Updated:** 2025-12-20
**Status:** FAILED - Abandoned in favor of Phase 5 MVP (MusicXML direct upload)
**Priority:** N/A - No longer pursued
**Outcome:** Pivot to user-side PDF conversion + MusicXML upload
