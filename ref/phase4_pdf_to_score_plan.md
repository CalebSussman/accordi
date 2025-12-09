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
- [ ] User can upload a PDF file
- [ ] Backend processes PDF with Audiveris
- [ ] MusicXML is returned to frontend
- [ ] OSMD displays the score on the page
- [ ] Error messages show when something fails
- [ ] Works end-to-end in production

## Next Phases (Future)

- **Phase 5:** Add accordion layout selection
- **Phase 6:** Implement note-to-button mapping
- **Phase 7:** Add interactive fingering visualization
- **Phase 8:** MIDI playback and export

---

**Created:** 2025-12-08
**Status:** Planning
**Priority:** High - Core functionality blocker
