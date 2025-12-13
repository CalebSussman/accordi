"""
Akkordio Backend - Pydantic Models

This module defines all Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Upload status")


class ProcessRequest(BaseModel):
    """Request model for processing configuration."""
    treble_layout: str = Field(
        default="c_system_5row_standard",
        description="Treble (right-hand) layout ID"
    )
    bass_layout: str = Field(
        default="stradella_120_standard",
        description="Bass (left-hand) layout ID"
    )
    omr_engine: str = Field(
        default="oemer",
        description="OMR engine to use: 'oemer' (better for photos/scans) or 'audiveris' (better for clean PDFs)"
    )
    options: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional processing options"
    )


class ProcessResponse(BaseModel):
    """Response model for processing start."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Processing status")
    progress: int = Field(..., description="Progress percentage (0-100)")
    message: str = Field(..., description="Status message")


class JobStatus(BaseModel):
    """Model for job status tracking."""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(
        ...,
        description="Current status: uploaded, processing, completed, failed"
    )
    progress: int = Field(..., description="Progress percentage (0-100)")
    message: str = Field(..., description="Current status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Job completion timestamp"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if status is failed"
    )


class ButtonPosition(BaseModel):
    """Model for accordion button position."""
    row: int = Field(..., description="Button row number")
    column: int = Field(..., description="Button column number")
    midi: int = Field(..., description="MIDI note number")
    note: str = Field(..., description="Note name (e.g., 'C4', 'F#3')")


class TrebleEvent(BaseModel):
    """Model for treble (right-hand) note event."""
    measure: int = Field(..., description="Measure number")
    beat: float = Field(..., description="Beat position in measure")
    duration: float = Field(..., description="Note duration in quarter notes")
    midi: int = Field(..., description="MIDI note number")
    note: str = Field(..., description="Note name")
    octave: int = Field(..., description="Octave number")
    button_positions: List[ButtonPosition] = Field(
        ...,
        description="Possible button positions for this note"
    )
    selected_position: Optional[ButtonPosition] = Field(
        default=None,
        description="Selected optimal button position"
    )
    dynamics: Optional[str] = Field(
        default=None,
        description="Dynamic marking (pp, p, mf, f, ff, etc.)"
    )
    articulation: Optional[str] = Field(
        default=None,
        description="Articulation marking (staccato, legato, etc.)"
    )


class ChordButton(BaseModel):
    """Model for Stradella bass chord button."""
    row: int = Field(..., description="Button row number")
    column: int = Field(..., description="Button column number")
    chord_type: str = Field(
        ...,
        description="Chord type: major, minor, seventh, diminished"
    )
    root: str = Field(..., description="Chord root note")
    notes: List[str] = Field(..., description="Notes in the chord")
    midi: List[int] = Field(..., description="MIDI note numbers")
    label: str = Field(..., description="Button label (e.g., 'CM', 'Am')")


class BassEvent(BaseModel):
    """Model for bass (left-hand) event."""
    measure: int = Field(..., description="Measure number")
    beat: float = Field(..., description="Beat position in measure")
    duration: float = Field(..., description="Event duration in quarter notes")
    event_type: str = Field(
        ...,
        description="Event type: single_note, chord"
    )
    midi: List[int] = Field(..., description="MIDI note numbers")
    notes: List[str] = Field(..., description="Note names")
    chord_type: Optional[str] = Field(
        default=None,
        description="Chord type if event is a chord"
    )
    root: Optional[str] = Field(
        default=None,
        description="Chord root if event is a chord"
    )
    button_position: Optional[ButtonPosition] = Field(
        default=None,
        description="Button position for single note"
    )
    chord_button: Optional[ChordButton] = Field(
        default=None,
        description="Chord button for Stradella system"
    )


class MusicMetadata(BaseModel):
    """Model for music score metadata."""
    title: Optional[str] = Field(default=None, description="Score title")
    composer: Optional[str] = Field(default=None, description="Composer name")
    key_signature: Optional[str] = Field(
        default=None,
        description="Key signature"
    )
    time_signature: Optional[str] = Field(
        default=None,
        description="Time signature (e.g., '4/4', '3/4')"
    )
    tempo: Optional[int] = Field(
        default=None,
        description="Tempo in BPM"
    )
    total_measures: Optional[int] = Field(
        default=None,
        description="Total number of measures"
    )


class MappingResult(BaseModel):
    """Model for complete mapping result."""
    job_id: str = Field(..., description="Unique job identifier")
    treble_events: List[TrebleEvent] = Field(
        ...,
        description="Treble (right-hand) note events"
    )
    bass_events: List[BassEvent] = Field(
        ...,
        description="Bass (left-hand) events"
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Score metadata and processing info"
    )
    treble_layout_id: Optional[str] = Field(
        default=None,
        description="Used treble layout ID"
    )
    bass_layout_id: Optional[str] = Field(
        default=None,
        description="Used bass layout ID"
    )


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    job_id: Optional[str] = Field(
        default=None,
        description="Related job ID if applicable"
    )
