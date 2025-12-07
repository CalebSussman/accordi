"""
Akkordio Backend - FastAPI Application Entry Point

This module provides the main FastAPI server for the Akkordio application,
handling PDF uploads, OMR processing, and accordion fingering mapping.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Optional
import aiofiles
import os
import uuid
from datetime import datetime
from pathlib import Path

from models import (
    UploadResponse,
    ProcessRequest,
    ProcessResponse,
    MappingResult,
    ErrorResponse,
    JobStatus
)

# Initialize FastAPI app
app = FastAPI(
    title="Akkordio API",
    description="Backend API for accordion fingering visualization",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://akkordio.github.io",  # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# In-memory job storage (replace with database in production)
jobs: Dict[str, JobStatus] = {}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify server is running.

    Returns:
        Dict containing status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "akkordio-backend"
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    """
    Accept PDF file upload and store temporarily.

    Args:
        file: PDF file from user

    Returns:
        UploadResponse with job_id and file info

    Raises:
        HTTPException: If file is not PDF or too large
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    # Validate file size (10MB max)
    file_size = 0
    temp_file = await file.read()
    file_size = len(temp_file)

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save file
    file_path = UPLOAD_DIR / f"{job_id}.pdf"
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(temp_file)

    # Initialize job status
    jobs[job_id] = JobStatus(
        job_id=job_id,
        status="uploaded",
        progress=0,
        message="File uploaded successfully",
        created_at=datetime.utcnow()
    )

    return UploadResponse(
        job_id=job_id,
        filename=file.filename,
        size=file_size,
        status="uploaded"
    )


@app.post("/process/{job_id}", response_model=ProcessResponse)
async def process_score(
    job_id: str,
    request: ProcessRequest,
    background_tasks: BackgroundTasks
) -> ProcessResponse:
    """
    Start OMR processing and fingering mapping for uploaded PDF.

    Args:
        job_id: Unique job identifier
        request: Processing configuration (layouts, etc.)
        background_tasks: FastAPI background tasks

    Returns:
        ProcessResponse with initial status

    Raises:
        HTTPException: If job_id not found
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    # Update job status
    jobs[job_id].status = "processing"
    jobs[job_id].progress = 10
    jobs[job_id].message = "Starting OMR processing..."

    # TODO: Add background task for actual processing
    # background_tasks.add_task(process_pdf_background, job_id, request)

    return ProcessResponse(
        job_id=job_id,
        status="processing",
        progress=10,
        message="Processing started"
    )


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str) -> JobStatus:
    """
    Check processing status of a job.

    Args:
        job_id: Unique job identifier

    Returns:
        JobStatus with current progress

    Raises:
        HTTPException: If job_id not found
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    return jobs[job_id]


@app.get("/results/{job_id}", response_model=MappingResult)
async def get_results(job_id: str) -> MappingResult:
    """
    Get processed data and accordion mappings.

    Args:
        job_id: Unique job identifier

    Returns:
        MappingResult with complete fingering data

    Raises:
        HTTPException: If job not found or not completed
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )

    if jobs[job_id].status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed yet. Current status: {jobs[job_id].status}"
        )

    # TODO: Load actual results from processed directory
    result_path = PROCESSED_DIR / f"{job_id}_result.json"

    if not result_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Results for job {job_id} not found"
        )

    # Return placeholder for now
    return MappingResult(
        job_id=job_id,
        treble_events=[],
        bass_events=[],
        metadata={}
    )


@app.get("/midi/{job_id}")
async def get_midi(job_id: str) -> FileResponse:
    """
    Download generated MIDI file.

    Args:
        job_id: Unique job identifier

    Returns:
        FileResponse with MIDI file

    Raises:
        HTTPException: If file not found
    """
    midi_path = PROCESSED_DIR / f"{job_id}.mid"

    if not midi_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"MIDI file for job {job_id} not found"
        )

    return FileResponse(
        midi_path,
        media_type="audio/midi",
        filename=f"akkordio_{job_id}.mid"
    )


@app.get("/musicxml/{job_id}")
async def get_musicxml(job_id: str) -> FileResponse:
    """
    Download MusicXML file.

    Args:
        job_id: Unique job identifier

    Returns:
        FileResponse with MusicXML file

    Raises:
        HTTPException: If file not found
    """
    xml_path = PROCESSED_DIR / f"{job_id}.musicxml"

    if not xml_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"MusicXML file for job {job_id} not found"
        )

    return FileResponse(
        xml_path,
        media_type="application/xml",
        filename=f"akkordio_{job_id}.musicxml"
    )


@app.get("/layouts/treble")
async def list_treble_layouts() -> Dict[str, list]:
    """
    List available treble (right-hand) accordion layouts.

    Returns:
        Dict with list of available layout IDs
    """
    layouts_dir = Path("layouts/treble")
    layouts = []

    if layouts_dir.exists():
        layouts = [f.stem for f in layouts_dir.glob("*.json")]

    return {"layouts": layouts}


@app.get("/layouts/bass")
async def list_bass_layouts() -> Dict[str, list]:
    """
    List available bass (left-hand) accordion layouts.

    Returns:
        Dict with list of available layout IDs
    """
    layouts_dir = Path("layouts/bass")
    layouts = []

    if layouts_dir.exists():
        layouts = [f.stem for f in layouts_dir.glob("*.json")]

    return {"layouts": layouts}


@app.get("/layouts/treble/{layout_id}")
async def get_treble_layout(layout_id: str) -> Dict:
    """
    Get specific treble layout configuration.

    Args:
        layout_id: Layout identifier

    Returns:
        Dict containing layout configuration

    Raises:
        HTTPException: If layout not found
    """
    layout_path = Path(f"layouts/treble/{layout_id}.json")

    if not layout_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Treble layout '{layout_id}' not found"
        )

    async with aiofiles.open(layout_path, 'r') as f:
        import json
        content = await f.read()
        return json.loads(content)


@app.get("/layouts/bass/{layout_id}")
async def get_bass_layout(layout_id: str) -> Dict:
    """
    Get specific bass layout configuration.

    Args:
        layout_id: Layout identifier

    Returns:
        Dict containing layout configuration

    Raises:
        HTTPException: If layout not found
    """
    layout_path = Path(f"layouts/bass/{layout_id}.json")

    if not layout_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Bass layout '{layout_id}' not found"
        )

    async with aiofiles.open(layout_path, 'r') as f:
        import json
        content = await f.read()
        return json.loads(content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
