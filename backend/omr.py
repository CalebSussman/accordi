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
import aiohttp
import aiofiles
from functools import lru_cache

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
        self.audiveris_api_url = os.getenv("AUDIVERIS_API_URL")
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
        Check if Audiveris is available via Cloud Run or Docker.

        Raises:
            OMRError: If neither Cloud Run nor Docker is available
        """
        if self.audiveris_api_url:
            logger.info(f"Using Audiveris via Cloud Run: {self.audiveris_api_url}")
            return

        # Check if Docker is available
        docker_path = shutil.which("docker")
        if not docker_path:
            logger.error("Docker not found and AUDIVERIS_API_URL not configured")
            raise OMRError(
                "Audiveris not available. Configure AUDIVERIS_API_URL for Cloud Run "
                "or install Docker with the jbarthelemy/audiveris image."
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

        OEMER requires image input, so we convert PDF to PNG first.

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
            # OEMER only accepts images, not PDFs
            # Convert PDF to PNG first using pdf2image
            try:
                from pdf2image import convert_from_path
            except ImportError:
                raise OMRError(
                    "pdf2image not installed. Please install with: pip install pdf2image"
                )

            logger.info(f"Converting PDF to image for OEMER: {pdf_path}")

            # Convert first page of PDF to image
            images = convert_from_path(str(pdf_path), first_page=1, last_page=1, dpi=300)

            if not images:
                raise OMRError("Failed to convert PDF to image")

            # Save as PNG
            image_path = output_dir / f"{pdf_path.stem}.png"
            images[0].save(image_path, 'PNG')

            logger.info(f"Converted PDF to image: {image_path}")

            # OEMER generates filename based on input
            musicxml_path = output_dir / f"{pdf_path.stem}.musicxml"

            logger.info(f"Running OEMER CLI on {image_path}")

            # Run OEMER as command-line tool
            # Command: oemer <input_image> -o <output_dir>
            process = await asyncio.create_subprocess_exec(
                "oemer",
                str(image_path),
                "-o", str(output_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            # Clean up temporary image
            if image_path.exists():
                image_path.unlink()

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
        Process PDF with Audiveris engine via Cloud Run (preferred) or Docker.

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
            if self.audiveris_api_url:
                return await self._process_with_audiveris_api(
                    pdf_path=pdf_path,
                    output_dir=output_dir,
                    timeout=timeout
                )

            return await self._process_with_audiveris_docker(
                pdf_path=pdf_path,
                output_dir=output_dir,
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Audiveris processing timed out after {timeout} seconds")
            raise OMRError(
                f"Processing timed out after {timeout} seconds. "
                f"The PDF may be too large or complex."
            )
        except Exception as e:
            logger.error(f"Unexpected error during Audiveris processing: {e}")
            raise OMRError(f"Audiveris processing failed: {str(e)}")

    async def _process_with_audiveris_api(
        self,
        pdf_path: Path,
        output_dir: Path,
        timeout: int
    ) -> Tuple[Path, dict]:
        """
        Process PDF with Audiveris Cloud Run API.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output files
            timeout: Maximum processing time in seconds

        Returns:
            Tuple of (musicxml_path, metadata_dict)

        Raises:
            OMRError: If processing fails
        """
        api_url = self.audiveris_api_url
        if not api_url:
            raise OMRError("AUDIVERIS_API_URL not configured")

        default_filename = f"{pdf_path.stem}.mxl"
        try:
            logger.info(f"Calling Audiveris Cloud Run at {api_url}")

            headers = {}
            auth_header = self._get_audiveris_auth_header(api_url)
            if auth_header:
                headers["Authorization"] = auth_header

            async with aiohttp.ClientSession(headers=headers or None) as session:
                with pdf_path.open("rb") as pdf_file:
                    form = aiohttp.FormData()
                    form.add_field(
                        "file",
                        pdf_file,
                        filename=pdf_path.name,
                        content_type="application/pdf"
                    )

                    response_timeout = aiohttp.ClientTimeout(total=timeout)
                    async with session.post(
                        f"{api_url}/process",
                        data=form,
                        timeout=response_timeout
                    ) as resp:
                        if resp.status != 200:
                            error = await resp.text()
                            logger.error(
                                "Audiveris API error %s: %s",
                                resp.status,
                                error
                            )
                            raise OMRError(
                                f"Audiveris API failed with status {resp.status}: {error}"
                            )

                        disposition = resp.headers.get("content-disposition", "")
                        filename = default_filename
                        if "filename=" in disposition:
                            filename = disposition.split("filename=")[-1].strip().strip('"')
                        if not filename:
                            filename = default_filename

                        musicxml_path = output_dir / filename

                        async with aiofiles.open(musicxml_path, 'wb') as out_file:
                            await out_file.write(await resp.read())

            if not musicxml_path.exists():
                raise OMRError("Audiveris API completed but no output file was saved")

            metadata = {
                "engine": "audiveris",
                "success": True,
                "warnings": [],
                "errors": [],
                "source": "cloud_run"
            }

            logger.info("Audiveris Cloud Run processing completed: %s", musicxml_path)
            return musicxml_path, metadata

        except asyncio.TimeoutError:
            logger.error("Audiveris API timeout after %s seconds", timeout)
            raise OMRError("Audiveris Cloud Run processing timed out")
        except aiohttp.ClientError as e:
            logger.error("Audiveris API client error: %s", e)
            raise OMRError(f"Audiveris API client error: {e}")
        except Exception as e:
            logger.error("Unexpected Audiveris API error: %s", e)
            raise OMRError(f"Audiveris Cloud Run processing failed: {e}")

    @lru_cache(maxsize=1)
    def _get_audiveris_auth_header(self, api_url: str) -> Optional[str]:
        """
        Build Authorization header for Audiveris Cloud Run if required.

        Priority:
        1. AUDIVERIS_API_BEARER_TOKEN (explicit token)
        2. AUDIVERIS_REQUIRE_AUTH=true with ID token from service account/default creds
        3. Otherwise, no auth header
        """
        explicit_token = os.getenv("AUDIVERIS_API_BEARER_TOKEN")
        if explicit_token:
            return f"Bearer {explicit_token}"

        require_auth = os.getenv("AUDIVERIS_REQUIRE_AUTH", "false").lower() == "true"
        if not require_auth:
            return None

        audience = os.getenv("AUDIVERIS_API_AUDIENCE", api_url)
        service_account_path = os.getenv("AUDIVERIS_SERVICE_ACCOUNT_JSON")

        try:
            from google.auth.transport.requests import Request as GoogleAuthRequest
            from google.oauth2 import service_account
            from google.auth import default as google_auth_default
            from google.auth import jwt
        except ImportError as exc:
            raise OMRError(
                "AUDIVERIS_REQUIRE_AUTH is true but google-auth is not installed. "
                "Install google-auth and requests or provide AUDIVERIS_API_BEARER_TOKEN."
            ) from exc

        credentials = None
        if service_account_path:
            credentials = service_account.IDTokenCredentials.from_service_account_file(
                service_account_path,
                target_audience=audience
            )
        else:
            default_creds, _ = google_auth_default()
            if hasattr(default_creds, "with_claims"):
                credentials = default_creds.with_claims(audience=audience)
            else:
                raise OMRError(
                    "Could not derive ID token from default credentials. "
                    "Set AUDIVERIS_SERVICE_ACCOUNT_JSON to a service account key file."
                )

        credentials.refresh(GoogleAuthRequest())
        if not credentials.token:
            raise OMRError("Failed to acquire ID token for Audiveris API.")

        return f"Bearer {credentials.token}"

    async def _process_with_audiveris_docker(
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
        metadata["source"] = "docker"

        return musicxml_path, metadata

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
