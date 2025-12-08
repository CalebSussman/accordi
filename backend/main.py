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

# Import processing modules
from omr import create_omr_processor
from parser import create_parser
from layout_generator import generate_layout, get_preset_layout
from treble_mapping import create_treble_mapper
from bass_mapping import create_bass_mapper
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "https://calebsussman.github.io",  # GitHub Pages
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


async def process_pdf_background(job_id: str, config: ProcessRequest):
    """
    Background task to process PDF through complete pipeline.

    Pipeline:
    1. OMR: PDF → MusicXML (Audiveris)
    2. Parse: MusicXML → Musical events (music21)
    3. Generate layouts: Based on user configuration
    4. Map: Musical events → Button positions
    5. Save results

    Args:
        job_id: Unique job identifier
        config: Processing configuration
    """
    try:
        pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
        output_dir = PROCESSED_DIR / job_id
        output_dir.mkdir(exist_ok=True)

        logger.info(f"Starting processing for job {job_id}")

        # Update status: OMR Processing
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 10
        jobs[job_id].message = "Converting PDF to MusicXML..."

        # Step 1: OMR Processing
        omr_processor = create_omr_processor()
        musicxml_path, omr_metadata = await omr_processor.process_pdf(
            pdf_path,
            output_dir
        )

        jobs[job_id].progress = 30
        jobs[job_id].message = "Parsing music notation..."

        # Step 2: Parse MusicXML
        parser = create_parser()
        treble_events, bass_events, music_metadata = await parser.parse_musicxml(
            musicxml_path
        )

        jobs[job_id].progress = 50
        jobs[job_id].message = "Generating keyboard layouts..."

        # Step 3: Generate Layouts
        # Get layout configuration from request
        treble_layout_config = config.options.get("treble_layout", {})
        bass_layout_config = config.options.get("bass_layout", {})

        # Use preset or custom configuration
        if "preset" in treble_layout_config:
            treble_layout = get_preset_layout(treble_layout_config["preset"])
        else:
            treble_layout = generate_layout(
                system_type=treble_layout_config.get("system", "c-system"),
                rows=treble_layout_config.get("rows", 5),
                columns=treble_layout_config.get("columns", 12),
                start_midi=treble_layout_config.get("start_midi", 48)
            )

        if "preset" in bass_layout_config:
            bass_layout = get_preset_layout(bass_layout_config["preset"])
        else:
            bass_layout = generate_layout(
                system_type=bass_layout_config.get("system", "stradella"),
                rows=bass_layout_config.get("rows"),
                columns=bass_layout_config.get("columns", 20),
                start_midi=bass_layout_config.get("start_midi")
            )

        jobs[job_id].progress = 60
        jobs[job_id].message = "Mapping notes to buttons..."

        # Step 4: Map Events to Buttons
        treble_mapper = create_treble_mapper(treble_layout)
        mapped_treble_events = treble_mapper.map_events(treble_events)

        bass_mapper = create_bass_mapper(bass_layout)
        mapped_bass_events = bass_mapper.map_events(bass_events)

        jobs[job_id].progress = 80
        jobs[job_id].message = "Finalizing results..."

        # Validate mappings
        treble_validation = treble_mapper.validate_mapping(mapped_treble_events)
        bass_validation = bass_mapper.validate_mapping(mapped_bass_events)

        # Step 5: Save Results
        result = {
            "job_id": job_id,
            "treble_events": mapped_treble_events,
            "bass_events": mapped_bass_events,
            "metadata": {
                **music_metadata,
                "omr_warnings": omr_metadata.get("warnings", []),
                "treble_layout": treble_layout["system"],
                "bass_layout": bass_layout["system"],
                "treble_mapping_success": treble_validation["success_rate"],
                "bass_mapping_success": bass_validation["success_rate"]
            },
            "treble_layout": treble_layout,
            "bass_layout": bass_layout,
            "validation": {
                "treble": treble_validation,
                "bass": bass_validation
            }
        }

        # Save to file
        result_path = output_dir / "result.json"
        async with aiofiles.open(result_path, 'w') as f:
            await f.write(json.dumps(result, indent=2))

        # Update job status
        jobs[job_id].status = "completed"
        jobs[job_id].progress = 100
        jobs[job_id].message = "Processing complete"
        jobs[job_id].completed_at = datetime.utcnow()

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(e)
        jobs[job_id].message = f"Processing failed: {str(e)}"


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

    # Start background processing
    background_tasks.add_task(process_pdf_background, job_id, request)

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

    # Load actual results from processed directory
    result_path = PROCESSED_DIR / job_id / "result.json"

    if not result_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Results for job {job_id} not found"
        )

    # Read and return results
    async with aiofiles.open(result_path, 'r') as f:
        content = await f.read()
        result_data = json.loads(content)

    return result_data


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


@app.get("/layouts/presets")
async def list_layout_presets() -> Dict:
    """
    List available preset layout configurations.

    Returns:
        Dict with available presets for treble and bass
    """
    from layout_generator import PRESET_CONFIGS

    treble_presets = [
        name for name, config in PRESET_CONFIGS.items()
        if config["type"] in ["c-system", "b-system"]
    ]

    bass_presets = [
        name for name, config in PRESET_CONFIGS.items()
        if config["type"] in ["stradella", "freebass-c", "freebass-b"]
    ]

    return {
        "treble": treble_presets,
        "bass": bass_presets,
        "all": list(PRESET_CONFIGS.keys())
    }


@app.get("/layouts/preset/{preset_name}")
async def get_preset_layout_endpoint(preset_name: str) -> Dict:
    """
    Get a dynamically generated layout from a preset.

    Args:
        preset_name: Preset name (e.g., 'c_system_5row', 'stradella_120')

    Returns:
        Generated layout configuration

    Raises:
        HTTPException: If preset not found
    """
    try:
        layout = get_preset_layout(preset_name)
        return layout
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.post("/layouts/generate")
async def generate_custom_layout(config: Dict) -> Dict:
    """
    Generate a custom layout dynamically.

    Args:
        config: Layout configuration dict with:
            - system_type: 'c-system', 'b-system', 'freebass-c', 'freebass-b', 'stradella'
            - rows: Number of rows (optional for stradella)
            - columns: Number of columns
            - start_midi: Starting MIDI note

    Returns:
        Generated layout configuration

    Raises:
        HTTPException: If invalid configuration
    """
    try:
        layout = generate_layout(**config)
        return layout
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid layout configuration: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
