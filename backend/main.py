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
import io
import zipfile
import xml.etree.ElementTree as ET
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


def _layout_from_request(layout_id: str) -> Dict:
    """Resolve a preset layout ID into generated layout data."""
    try:
        return get_preset_layout(layout_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _mxl_rootfile_name(zip_file: zipfile.ZipFile) -> Optional[str]:
    """Resolve the score XML path inside an MXL archive."""
    try:
        with zip_file.open("META-INF/container.xml") as container_file:
            container_tree = ET.parse(container_file)
        root = container_tree.getroot()
        for element in root.iter():
            if element.tag.endswith("rootfile"):
                full_path = element.attrib.get("full-path")
                if full_path and full_path in zip_file.namelist():
                    return full_path
    except (KeyError, ET.ParseError):
        pass

    xml_files = [
        name for name in zip_file.namelist()
        if name.endswith(".xml") and not name.startswith("META-INF/")
    ]
    return xml_files[0] if xml_files else None


async def _write_normalized_musicxml(
    filename: str,
    content: bytes,
    musicxml_path: Path
) -> None:
    """Store plain MusicXML bytes from a MusicXML or compressed MXL upload."""
    if filename.endswith(".mxl"):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                rootfile_name = _mxl_rootfile_name(zip_file)
                if not rootfile_name:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid .mxl file: no MusicXML content found"
                    )
                musicxml_content = zip_file.read(rootfile_name)
                logger.info(f"Extracted MusicXML from .mxl: {rootfile_name}")
        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid .mxl file: not a valid ZIP archive"
            ) from exc
    else:
        musicxml_content = content

    async with aiofiles.open(musicxml_path, 'wb') as f:
        await f.write(musicxml_content)


async def process_musicxml_file(
    job_id: str,
    musicxml_path: Path,
    config: Optional[ProcessRequest] = None,
    omr_metadata: Optional[Dict] = None
) -> Dict:
    """
    Shared MusicXML parse/layout/map/save pipeline.

    This keeps direct MusicXML upload and future PDF-to-MusicXML processing on
    the same result contract.
    """
    config = config or ProcessRequest()
    omr_metadata = omr_metadata or {}
    output_dir = PROCESSED_DIR / job_id
    output_dir.mkdir(exist_ok=True)

    if job_id in jobs:
        jobs[job_id].status = "processing"
        jobs[job_id].progress = 30
        jobs[job_id].message = "Parsing music notation..."

    parser = create_parser()
    treble_events, bass_events, music_metadata = await parser.parse_musicxml(
        musicxml_path
    )

    if job_id in jobs:
        jobs[job_id].progress = 50
        jobs[job_id].message = "Generating keyboard layouts..."

    treble_layout_id = config.treble_layout or "b_system_5row"
    bass_layout_id = config.bass_layout or "stradella_120"
    treble_layout = _layout_from_request(treble_layout_id)
    bass_layout = _layout_from_request(bass_layout_id)

    if job_id in jobs:
        jobs[job_id].progress = 70
        jobs[job_id].message = "Mapping notes to buttons..."

    treble_mapper = create_treble_mapper(treble_layout)
    mapped_treble_events = treble_mapper.map_events(treble_events)

    bass_mapper = create_bass_mapper(bass_layout)
    mapped_bass_events = bass_mapper.map_events(bass_events)

    treble_validation = treble_mapper.validate_mapping(
        mapped_treble_events,
        treble_events
    )
    bass_validation = bass_mapper.validate_mapping(
        mapped_bass_events,
        bass_events
    )
    treble_validation["layout_id"] = treble_layout_id
    bass_validation["layout_id"] = bass_layout_id

    result = {
        "job_id": job_id,
        "treble_events": mapped_treble_events,
        "bass_events": mapped_bass_events,
        "metadata": {
            **music_metadata,
            "omr_warnings": omr_metadata.get("warnings", []),
            "treble_layout": treble_layout["system"],
            "bass_layout": bass_layout["system"],
            "treble_layout_id": treble_layout_id,
            "bass_layout_id": bass_layout_id,
            "treble_mapping_success": treble_validation["success_rate"],
            "bass_mapping_success": bass_validation["success_rate"]
        },
        "treble_layout_id": treble_layout_id,
        "bass_layout_id": bass_layout_id,
        "treble_layout": treble_layout,
        "bass_layout": bass_layout,
        "validation": {
            "treble": treble_validation,
            "bass": bass_validation
        }
    }

    result_path = output_dir / "result.json"
    async with aiofiles.open(result_path, 'w') as f:
        await f.write(json.dumps(result, indent=2))

    if job_id in jobs:
        jobs[job_id].status = "completed"
        jobs[job_id].progress = 100
        jobs[job_id].message = "Processing complete"
        jobs[job_id].completed_at = datetime.utcnow()

    return result


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
        # Use engine from config, default to oemer
        engine = config.omr_engine if config.omr_engine in ["oemer", "audiveris"] else "oemer"
        omr_processor = create_omr_processor(engine=engine)
        musicxml_path, omr_metadata = await omr_processor.process_pdf(
            pdf_path,
            output_dir
        )

        jobs[job_id].progress = 30
        jobs[job_id].message = "Parsing music notation..."

        await process_musicxml_file(
            job_id,
            musicxml_path,
            config=config,
            omr_metadata=omr_metadata
        )

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
    # Try job-specific directory first (new structure)
    xml_path = PROCESSED_DIR / job_id / f"{job_id}.musicxml"

    # Fallback to old structure
    if not xml_path.exists():
        xml_path = PROCESSED_DIR / f"{job_id}.musicxml"

    if not xml_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"MusicXML file for job {job_id} not found"
        )

    return FileResponse(
        xml_path,
        media_type="application/vnd.recordare.musicxml+xml",
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


@app.post("/upload_musicxml")
async def upload_musicxml(file: UploadFile = File(...)) -> Dict:
    """
    Accept MusicXML file upload and return it for OSMD display.

    This is a simplified MVP endpoint that bypasses OMR processing.
    User provides pre-converted MusicXML files.

    Args:
        file: MusicXML file (.mxl or .musicxml)

    Returns:
        Dict with job_id and musicxml_url for frontend

    Raises:
        HTTPException: If file is not MusicXML or too large
    """
    # Validate file type
    if not (file.filename.endswith('.mxl') or file.filename.endswith('.musicxml') or file.filename.endswith('.xml')):
        raise HTTPException(
            status_code=400,
            detail="Only MusicXML files (.mxl, .musicxml, .xml) are accepted"
        )

    # Validate file size (5MB max for MusicXML)
    temp_file = await file.read()
    file_size = len(temp_file)

    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 5MB limit"
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Create output directory
    output_dir = PROCESSED_DIR / job_id
    output_dir.mkdir(exist_ok=True)

    musicxml_path = output_dir / f"{job_id}.musicxml"
    await _write_normalized_musicxml(file.filename, temp_file, musicxml_path)

    jobs[job_id] = JobStatus(
        job_id=job_id,
        status="processing",
        progress=10,
        message="MusicXML file uploaded successfully",
        created_at=datetime.utcnow()
    )

    try:
        result = await process_musicxml_file(
            job_id,
            musicxml_path,
            config=ProcessRequest()
        )
    except HTTPException:
        jobs[job_id].status = "failed"
        jobs[job_id].message = "Processing failed"
        raise
    except Exception as exc:
        logger.error(f"MusicXML job {job_id} failed: {exc}", exc_info=True)
        jobs[job_id].status = "failed"
        jobs[job_id].error = str(exc)
        jobs[job_id].message = f"Processing failed: {str(exc)}"
        raise HTTPException(
            status_code=500,
            detail=f"MusicXML processing failed: {str(exc)}"
        ) from exc

    logger.info(f"MusicXML processed: job_id={job_id}, size={file_size} bytes")

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "size": file_size,
        "status": "completed",
        "musicxml_url": f"/musicxml/{job_id}",
        "results_url": f"/results/{job_id}",
        "validation": result["validation"],
        "message": "MusicXML mapped successfully"
    }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
