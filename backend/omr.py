"""
Akkordio Backend - OMR Integration

This module handles Optical Music Recognition using OEMER or Audiveris.
Converts PDF music scores to MusicXML format.
"""

import asyncio
import subprocess
import shutil
import os
from pathlib import Path
from typing import Optional, Tuple, Literal
import logging

logger = logging.getLogger(__name__)

# Type for OMR engine selection
OMREngine = Literal["oemer", "audiveris"]


class OMRError(Exception):
    """Custom exception for OMR-related errors."""
    pass


class OMRProcessor:
    """
    Handles PDF to MusicXML conversion using OEMER or Audiveris.

    Supports two OMR engines:
    - OEMER: Modern deep learning-based OMR (better for photos/scans)
    - Audiveris: Traditional OMR (better for clean PDFs)
    """

    def __init__(self, engine: OMREngine = "oemer"):
        """
        Initialize OMR processor.

        Args:
            engine: Which OMR engine to use ("oemer" or "audiveris")
        """
        self.engine = engine
        logger.info(f"Initializing OMR processor with engine: {engine}")

        if engine == "oemer":
            self._check_oemer_available()
        elif engine == "audiveris":
            self._check_audiveris_available()
        else:
            raise OMRError(f"Unknown OMR engine: {engine}")

    def _check_oemer_available(self) -> None:
        """
        Check if OEMER CLI is available.

        Raises:
            OMRError: If OEMER is not found
        """
        oemer_path = shutil.which("oemer")
        if not oemer_path:
            logger.error("OEMER CLI not found in PATH")
            raise OMRError(
                "OEMER not found. Please install with: pip install oemer"
            )
        logger.info(f"OEMER CLI available at: {oemer_path}")

    def _check_audiveris_available(self) -> None:
        """
        Check if Audiveris is available via Docker.

        Raises:
            OMRError: If Docker or Audiveris image is not available
        """
        # Check if Docker is available
        docker_path = shutil.which("docker")
        if not docker_path:
            logger.error("Docker not found")
            raise OMRError(
                "Docker not found. Audiveris requires Docker to be installed."
            )

        # Check if Audiveris Docker image is available
        try:
            result = subprocess.run(
                ["docker", "images", "-q", "jbarthelemy/audiveris:latest"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if not result.stdout.strip():
                logger.warning("Audiveris Docker image not found, will pull on first use")
        except Exception as e:
            logger.warning(f"Could not check for Audiveris Docker image: {e}")

        logger.info("Docker available for Audiveris")

    async def process_pdf(
        self,
        pdf_path: Path,
        output_dir: Path,
        timeout: int = 300
    ) -> Tuple[Path, dict]:
        """
        Process PDF file with selected OMR engine to generate MusicXML.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output files
            timeout: Maximum processing time in seconds (default: 5 minutes)

        Returns:
            Tuple of (musicxml_path, metadata_dict)

        Raises:
            OMRError: If processing fails
            FileNotFoundError: If PDF file doesn't exist
            asyncio.TimeoutError: If processing exceeds timeout
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting OMR processing with {self.engine} for: {pdf_path}")

        if self.engine == "oemer":
            return await self._process_with_oemer(pdf_path, output_dir, timeout)
        elif self.engine == "audiveris":
            return await self._process_with_audiveris(pdf_path, output_dir, timeout)
        else:
            raise OMRError(f"Unknown engine: {self.engine}")

    async def _process_with_oemer(
        self,
        pdf_path: Path,
        output_dir: Path,
        timeout: int
    ) -> Tuple[Path, dict]:
        """
        Process PDF with OEMER engine via CLI.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output files
            timeout: Maximum processing time in seconds

        Returns:
            Tuple of (musicxml_path, metadata_dict)

        Raises:
            OMRError: If processing fails
        """
        try:
            # OEMER generates filename based on input, outputs to specified directory
            # Format: {stem}.musicxml
            musicxml_path = output_dir / f"{pdf_path.stem}.musicxml"

            logger.info(f"Running OEMER CLI on {pdf_path}")

            # Run OEMER as command-line tool
            # Command: oemer <input_pdf> -o <output_dir>
            process = await asyncio.create_subprocess_exec(
                "oemer",
                str(pdf_path),
                "-o", str(output_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            # Check return code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"OEMER failed: {error_msg}")
                raise OMRError(
                    f"OEMER processing failed with code {process.returncode}: {error_msg}"
                )

            # Verify output file was created
            if not musicxml_path.exists():
                raise OMRError(f"OEMER completed but output file not found: {musicxml_path}")

            logger.info(f"OEMER processing completed: {musicxml_path}")

            # Build metadata
            metadata = {
                "engine": "oemer",
                "success": True,
                "warnings": [],
                "errors": []
            }

            return musicxml_path, metadata

        except asyncio.TimeoutError:
            logger.error(f"OEMER processing timed out after {timeout} seconds")
            raise OMRError(
                f"Processing timed out after {timeout} seconds. "
                f"The PDF may be too large or complex."
            )
        except FileNotFoundError:
            logger.error("OEMER command not found")
            raise OMRError("OEMER not found. Please install with: pip install oemer")
        except Exception as e:
            logger.error(f"Unexpected error during OEMER processing: {e}")
            raise OMRError(f"OEMER processing failed: {str(e)}")

    async def _process_with_audiveris(
        self,
        pdf_path: Path,
        output_dir: Path,
        timeout: int
    ) -> Tuple[Path, dict]:
        """
        Process PDF with Audiveris engine via Docker.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output files
            timeout: Maximum processing time in seconds

        Returns:
            Tuple of (musicxml_path, metadata_dict)

        Raises:
            OMRError: If processing fails
        """
        try:
            # Expected MusicXML output path
            musicxml_path = output_dir / f"{pdf_path.stem}.mxl"

            # Get absolute paths for Docker volume mounting
            pdf_abs = pdf_path.absolute()
            output_abs = output_dir.absolute()

            logger.info(f"Running Audiveris via Docker on {pdf_path}")

            # Docker command to run Audiveris
            # Mount input PDF and output directory as volumes
            docker_cmd = [
                "docker", "run", "--rm",
                "-v", f"{pdf_abs.parent}:/input:ro",
                "-v", f"{output_abs}:/output",
                "jbarthelemy/audiveris:latest",
                "-batch",
                "-export",
                "-output", "/output",
                f"/input/{pdf_abs.name}"
            ]

            # Run Docker command
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
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
                raise OMRError(
                    f"Audiveris processing failed with code {process.returncode}: {error_msg}"
                )

            # Verify output file was created
            if not musicxml_path.exists():
                # Try alternative extensions
                alt_path = output_dir / f"{pdf_path.stem}.musicxml"
                if alt_path.exists():
                    musicxml_path = alt_path
                else:
                    raise OMRError(
                        f"Audiveris completed but output file not found: {musicxml_path}"
                    )

            logger.info(f"Audiveris processing completed: {musicxml_path}")

            # Parse metadata from output
            metadata = self._parse_audiveris_output(stdout.decode('utf-8'))
            metadata["engine"] = "audiveris"

            return musicxml_path, metadata

        except asyncio.TimeoutError:
            logger.error(f"Audiveris processing timed out after {timeout} seconds")
            raise OMRError(
                f"Processing timed out after {timeout} seconds. "
                f"The PDF may be too large or complex."
            )
        except Exception as e:
            logger.error(f"Unexpected error during Audiveris processing: {e}")
            raise OMRError(f"Audiveris processing failed: {str(e)}")

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
def create_omr_processor(engine: OMREngine = "oemer") -> OMRProcessor:
    """
    Create and return an OMR processor instance.

    Args:
        engine: Which OMR engine to use ("oemer" or "audiveris")

    Returns:
        OMRProcessor instance
    """
    return OMRProcessor(engine=engine)
