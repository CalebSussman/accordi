"""
Akkordio Backend - OMR Integration

This module handles Optical Music Recognition using Audiveris CLI.
Converts PDF music scores to MusicXML format.
"""

import asyncio
import subprocess
import shutil
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AudiverisError(Exception):
    """Custom exception for Audiveris-related errors."""
    pass


class OMRProcessor:
    """
    Handles PDF to MusicXML conversion using Audiveris.

    Audiveris is an open-source OMR system that processes sheet music images
    and converts them to MusicXML format.
    """

    def __init__(self, audiveris_path: Optional[str] = None):
        """
        Initialize OMR processor.

        Args:
            audiveris_path: Path to Audiveris executable. If None, checks
                          AUDIVERIS_PATH env var, then assumes 'audiveris' is in PATH.
        """
        self.audiveris_path = audiveris_path or os.getenv('AUDIVERIS_PATH', 'audiveris')
        self._check_audiveris_available()

    def _check_audiveris_available(self) -> None:
        """
        Check if Audiveris is available in the system.

        Raises:
            AudiverisError: If Audiveris is not found
        """
        audiveris_executable = shutil.which(self.audiveris_path)
        if not audiveris_executable:
            logger.error("Audiveris not found in PATH")
            raise AudiverisError(
                f"Audiveris not found. Please install Audiveris and ensure it's in your PATH. "
                f"Looking for: {self.audiveris_path}"
            )

        logger.info(f"Audiveris found at: {audiveris_executable}")

    async def process_pdf(
        self,
        pdf_path: Path,
        output_dir: Path,
        timeout: int = 300
    ) -> Tuple[Path, dict]:
        """
        Process PDF file with Audiveris to generate MusicXML.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output files
            timeout: Maximum processing time in seconds (default: 5 minutes)

        Returns:
            Tuple of (musicxml_path, metadata_dict)

        Raises:
            AudiverisError: If processing fails
            FileNotFoundError: If PDF file doesn't exist
            asyncio.TimeoutError: If processing exceeds timeout
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Expected MusicXML output path
        musicxml_path = output_dir / f"{pdf_path.stem}.mxl"

        logger.info(f"Starting OMR processing for: {pdf_path}")

        try:
            # Run Audiveris CLI
            # Command: audiveris -batch -export <pdf_file>
            # This processes the PDF and exports to MusicXML (.mxl) format
            process = await asyncio.create_subprocess_exec(
                self.audiveris_path,
                "-batch",
                "-export",
                "-output",
                str(output_dir),
                str(pdf_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for process with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            # Check return code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Audiveris failed: {error_msg}")
                raise AudiverisError(
                    f"Audiveris processing failed with code {process.returncode}: {error_msg}"
                )

            # Verify output file was created
            if not musicxml_path.exists():
                # Try alternative extensions
                alt_path = output_dir / f"{pdf_path.stem}.musicxml"
                if alt_path.exists():
                    musicxml_path = alt_path
                else:
                    raise AudiverisError(
                        f"Audiveris completed but output file not found: {musicxml_path}"
                    )

            logger.info(f"OMR processing completed: {musicxml_path}")

            # Parse metadata from output
            metadata = self._parse_audiveris_output(stdout.decode('utf-8'))

            return musicxml_path, metadata

        except asyncio.TimeoutError:
            logger.error(f"OMR processing timed out after {timeout} seconds")
            raise AudiverisError(
                f"Processing timed out after {timeout} seconds. "
                f"The PDF may be too large or complex."
            )
        except Exception as e:
            logger.error(f"Unexpected error during OMR processing: {e}")
            raise AudiverisError(f"OMR processing failed: {str(e)}")

    def _parse_audiveris_output(self, output: str) -> dict:
        """
        Parse Audiveris output for metadata.

        Args:
            output: Audiveris stdout output

        Returns:
            Dictionary with processing metadata
        """
        metadata = {
            "success": True,
            "warnings": [],
            "errors": []
        }

        # Parse output for useful information
        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            if 'WARNING' in line.upper():
                metadata["warnings"].append(line)
            elif 'ERROR' in line.upper():
                metadata["errors"].append(line)

        return metadata

    async def validate_musicxml(self, musicxml_path: Path) -> bool:
        """
        Validate MusicXML file structure.

        Args:
            musicxml_path: Path to MusicXML file

        Returns:
            True if valid, False otherwise
        """
        if not musicxml_path.exists():
            return False

        try:
            # Check if file is compressed (.mxl) or uncompressed (.musicxml)
            if musicxml_path.suffix == '.mxl':
                # Compressed MusicXML - check if it's a valid zip
                import zipfile
                with zipfile.ZipFile(musicxml_path, 'r') as zip_ref:
                    # Check for required files
                    namelist = zip_ref.namelist()
                    if not any('META-INF' in name for name in namelist):
                        logger.warning("MusicXML missing META-INF")
                        return False
            else:
                # Uncompressed - basic XML validation
                import xml.etree.ElementTree as ET
                tree = ET.parse(musicxml_path)
                root = tree.getroot()

                # Check for score-partwise or score-timewise root
                if 'score' not in root.tag.lower():
                    logger.warning("Invalid MusicXML root element")
                    return False

            logger.info(f"MusicXML validation passed: {musicxml_path}")
            return True

        except Exception as e:
            logger.error(f"MusicXML validation failed: {e}")
            return False

    async def extract_preview_image(
        self,
        pdf_path: Path,
        output_path: Path,
        page: int = 1
    ) -> Optional[Path]:
        """
        Extract first page of PDF as preview image.

        Args:
            pdf_path: Path to PDF file
            output_path: Path for output image
            page: Page number to extract (default: 1)

        Returns:
            Path to preview image if successful, None otherwise
        """
        try:
            from PIL import Image
            import fitz  # PyMuPDF

            # Open PDF
            doc = fitz.open(pdf_path)

            if page > len(doc):
                page = 1

            # Get page
            pdf_page = doc[page - 1]

            # Render page to image
            pix = pdf_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Save preview
            img.save(output_path, "PNG")

            doc.close()

            logger.info(f"Preview image created: {output_path}")
            return output_path

        except ImportError:
            logger.warning("PyMuPDF not available for preview generation")
            return None
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return None


# Factory function for easy instantiation
def create_omr_processor(audiveris_path: Optional[str] = None) -> OMRProcessor:
    """
    Create and return an OMR processor instance.

    Args:
        audiveris_path: Optional path to Audiveris executable

    Returns:
        OMRProcessor instance
    """
    return OMRProcessor(audiveris_path=audiveris_path)
