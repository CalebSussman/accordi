"""
Audiveris Microservice for Cloud Run

Provides PDF-to-MusicXML conversion via Audiveris CLI.
Designed to run as a standalone Cloud Run service.
"""

import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audiveris-service")

app = FastAPI(
    title="Audiveris OMR API",
    description="Optical Music Recognition using Audiveris",
    version="1.0.0",
)

# Paths and configuration
AUDIVERIS_PATH = os.getenv("AUDIVERIS_PATH", "/opt/Audiveris/bin/Audiveris")
UPLOAD_DIR = Path("/tmp/uploads")
OUTPUT_DIR = Path("/tmp/output")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_TIMEOUT = int(os.getenv("AUDIVERIS_TIMEOUT", "300"))


def _find_output_file(job_id: str, output_path: Path) -> Optional[Path]:
    """Locate the MusicXML file produced by Audiveris."""
    mxl = output_path / f"{job_id}.mxl"
    if mxl.exists():
        return mxl
    xml = output_path / f"{job_id}.musicxml"
    if xml.exists():
        return xml
    return None


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "service": "audiveris-omr",
        "audiveris_available": Path(AUDIVERIS_PATH).exists(),
    }


@app.post("/process")
async def process_pdf(file: UploadFile = File(...)) -> FileResponse:
    """
    Process a PDF with Audiveris and return MusicXML.

    Args:
        file: Uploaded PDF file

    Returns:
        FileResponse with MusicXML (.mxl or .musicxml)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    job_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
    output_path = OUTPUT_DIR / job_id
    output_path.mkdir(exist_ok=True)

    try:
        async with aiofiles.open(pdf_path, "wb") as pdf_file:
            content = await file.read()
            await pdf_file.write(content)

        logger.info("Processing PDF %s with Audiveris", pdf_path)

        process = await asyncio.create_subprocess_exec(
            AUDIVERIS_PATH,
            "-batch",
            "-export",
            "-output",
            str(output_path),
            str(pdf_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=DEFAULT_TIMEOUT,
            )
        except asyncio.TimeoutError as exc:
            process.kill()
            raise HTTPException(
                status_code=504,
                detail=f"Processing timed out after {DEFAULT_TIMEOUT} seconds",
            ) from exc

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
            logger.error("Audiveris failed: %s", error_msg)
            raise HTTPException(
                status_code=500,
                detail=f"Audiveris processing failed: {error_msg}",
            )

        musicxml_path = _find_output_file(pdf_path.stem, output_path)
        if not musicxml_path:
            logger.error("Audiveris completed but no output file found for job %s", job_id)
            raise HTTPException(
                status_code=500,
                detail="Audiveris completed but no output file found",
            )

        logger.info("Audiveris processing completed: %s", musicxml_path)

        media_type = "application/vnd.recordare.musicxml+xml"
        filename = f"{pdf_path.stem}{musicxml_path.suffix}"
        return FileResponse(
            musicxml_path,
            media_type=media_type,
            filename=filename,
        )
    finally:
        # Cleanup input file; keep output for response
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except OSError:
                logger.warning("Failed to remove temp PDF %s", pdf_path)


@app.get("/")
async def root() -> dict:
    """API information endpoint."""
    return {
        "service": "Audiveris OMR API",
        "version": "1.0.0",
        "endpoints": {
            "POST /process": "Process PDF to MusicXML",
            "GET /health": "Health check",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
