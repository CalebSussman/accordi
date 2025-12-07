"""
Akkordio Backend - MusicXML Parser

This module uses music21 to parse MusicXML files and extract musical events
for treble and bass parts of accordion music.
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from music21 import converter, note, chord, stream, interval
from music21.stream import Score, Part

from models import TrebleEvent, BassEvent, MusicMetadata

logger = logging.getLogger(__name__)


class MusicXMLParser:
    """
    Parses MusicXML files and extracts treble and bass events.

    Uses music21 library for music analysis and event extraction.
    """

    def __init__(self):
        """Initialize the parser."""
        pass

    async def parse_musicxml(
        self,
        musicxml_path: Path
    ) -> Tuple[List[Dict], List[Dict], Dict]:
        """
        Parse MusicXML file and extract musical events.

        Args:
            musicxml_path: Path to MusicXML file (.mxl or .musicxml)

        Returns:
            Tuple of (treble_events, bass_events, metadata)

        Raises:
            Exception: If parsing fails
        """
        try:
            logger.info(f"Parsing MusicXML: {musicxml_path}")

            # Load the score using music21
            score = converter.parse(str(musicxml_path))

            # Extract metadata
            metadata = self._extract_metadata(score)
            logger.info(f"Metadata extracted: {metadata}")

            # Identify treble and bass parts
            treble_part, bass_part = self._identify_parts(score)

            # Extract events from each part
            treble_events = []
            bass_events = []

            if treble_part:
                treble_events = self._extract_treble_events(treble_part)
                logger.info(f"Extracted {len(treble_events)} treble events")

            if bass_part:
                bass_events = self._extract_bass_events(bass_part)
                logger.info(f"Extracted {len(bass_events)} bass events")

            return treble_events, bass_events, metadata

        except Exception as e:
            logger.error(f"MusicXML parsing failed: {e}")
            raise Exception(f"Failed to parse MusicXML: {str(e)}")

    def _extract_metadata(self, score: Score) -> Dict:
        """
        Extract metadata from the score.

        Args:
            score: music21 Score object

        Returns:
            Dictionary with metadata
        """
        metadata = {
            "title": None,
            "composer": None,
            "key_signature": None,
            "time_signature": None,
            "tempo": None,
            "total_measures": 0
        }

        try:
            # Title
            if score.metadata and score.metadata.title:
                metadata["title"] = score.metadata.title

            # Composer
            if score.metadata and score.metadata.composer:
                metadata["composer"] = score.metadata.composer

            # Get first part for time/key signatures
            parts = score.parts
            if parts:
                first_part = parts[0]

                # Key signature
                key_sigs = first_part.flatten().getElementsByClass('KeySignature')
                if key_sigs:
                    metadata["key_signature"] = str(key_sigs[0])

                # Time signature
                time_sigs = first_part.flatten().getElementsByClass('TimeSignature')
                if time_sigs:
                    ts = time_sigs[0]
                    metadata["time_signature"] = f"{ts.numerator}/{ts.denominator}"

                # Tempo
                tempos = first_part.flatten().getElementsByClass('MetronomeMark')
                if tempos:
                    metadata["tempo"] = int(tempos[0].number)

                # Total measures
                measures = first_part.getElementsByClass('Measure')
                if measures:
                    metadata["total_measures"] = len(measures)

        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")

        return metadata

    def _identify_parts(self, score: Score) -> Tuple[Optional[Part], Optional[Part]]:
        """
        Identify treble (right-hand) and bass (left-hand) parts.

        Args:
            score: music21 Score object

        Returns:
            Tuple of (treble_part, bass_part)
        """
        parts = score.parts

        if len(parts) == 0:
            logger.warning("No parts found in score")
            return None, None

        # For accordion scores, typically:
        # - First part (or higher clef) = treble/right hand
        # - Second part (or lower clef) = bass/left hand

        treble_part = None
        bass_part = None

        if len(parts) == 1:
            # Single part - treat as treble
            treble_part = parts[0]
            logger.info("Single part detected, treating as treble")

        elif len(parts) >= 2:
            # Multiple parts - identify by clef or range
            for i, part in enumerate(parts):
                clefs = part.flatten().getElementsByClass('Clef')
                if clefs:
                    clef = clefs[0]
                    if 'Treble' in str(type(clef)):
                        treble_part = part
                        logger.info(f"Part {i} identified as treble (treble clef)")
                    elif 'Bass' in str(type(clef)):
                        bass_part = part
                        logger.info(f"Part {i} identified as bass (bass clef)")

            # Fallback: first part = treble, second = bass
            if not treble_part and not bass_part:
                treble_part = parts[0]
                bass_part = parts[1] if len(parts) > 1 else None
                logger.info("Using fallback: part 0=treble, part 1=bass")

        return treble_part, bass_part

    def _extract_treble_events(self, part: Part) -> List[Dict]:
        """
        Extract note events from treble part.

        Args:
            part: music21 Part object for treble

        Returns:
            List of treble event dictionaries
        """
        events = []

        # Flatten the part to get all notes in sequence
        flat_notes = part.flatten().notesAndRests

        for element in flat_notes:
            # Skip rests
            if element.isRest:
                continue

            # Get measure number
            measure_num = element.measureNumber if element.measureNumber else 1

            # Get beat position
            beat_pos = float(element.beat) if hasattr(element, 'beat') else 0.0

            # Handle single notes
            if isinstance(element, note.Note):
                event = {
                    "measure": measure_num,
                    "beat": beat_pos,
                    "duration": float(element.quarterLength),
                    "midi": element.pitch.midi,
                    "note": element.pitch.nameWithOctave,
                    "octave": element.pitch.octave,
                    "dynamics": self._get_dynamics(element),
                    "articulation": self._get_articulation(element)
                }
                events.append(event)

            # Handle chords (multiple simultaneous notes)
            elif isinstance(element, chord.Chord):
                # For each note in the chord, create separate events
                for pitch in element.pitches:
                    event = {
                        "measure": measure_num,
                        "beat": beat_pos,
                        "duration": float(element.quarterLength),
                        "midi": pitch.midi,
                        "note": pitch.nameWithOctave,
                        "octave": pitch.octave,
                        "dynamics": self._get_dynamics(element),
                        "articulation": self._get_articulation(element)
                    }
                    events.append(event)

        logger.info(f"Extracted {len(events)} treble events")
        return events

    def _extract_bass_events(self, part: Part) -> List[Dict]:
        """
        Extract note and chord events from bass part.

        Args:
            part: music21 Part object for bass

        Returns:
            List of bass event dictionaries
        """
        events = []

        # Flatten the part to get all notes in sequence
        flat_notes = part.flatten().notesAndRests

        for element in flat_notes:
            # Skip rests
            if element.isRest:
                continue

            # Get measure number
            measure_num = element.measureNumber if element.measureNumber else 1

            # Get beat position
            beat_pos = float(element.beat) if hasattr(element, 'beat') else 0.0

            # Handle single notes
            if isinstance(element, note.Note):
                event = {
                    "measure": measure_num,
                    "beat": beat_pos,
                    "duration": float(element.quarterLength),
                    "event_type": "single_note",
                    "midi": [element.pitch.midi],
                    "notes": [element.pitch.nameWithOctave],
                    "chord_type": None,
                    "root": None
                }
                events.append(event)

            # Handle chords
            elif isinstance(element, chord.Chord):
                # Analyze chord to determine type
                chord_info = self._analyze_chord(element)

                event = {
                    "measure": measure_num,
                    "beat": beat_pos,
                    "duration": float(element.quarterLength),
                    "event_type": "chord",
                    "midi": [p.midi for p in element.pitches],
                    "notes": [p.nameWithOctave for p in element.pitches],
                    "chord_type": chord_info["type"],
                    "root": chord_info["root"]
                }
                events.append(event)

        logger.info(f"Extracted {len(events)} bass events")
        return events

    def _analyze_chord(self, chord_obj: chord.Chord) -> Dict:
        """
        Analyze chord to determine type and root.

        Args:
            chord_obj: music21 Chord object

        Returns:
            Dictionary with chord analysis
        """
        try:
            # Get chord root
            root = chord_obj.root().name

            # Determine chord quality
            chord_type = "major"  # default

            if chord_obj.isMajorTriad():
                chord_type = "major"
            elif chord_obj.isMinorTriad():
                chord_type = "minor"
            elif chord_obj.isDominantSeventh():
                chord_type = "seventh"
            elif chord_obj.isDiminishedTriad():
                chord_type = "diminished"
            elif chord_obj.isAugmentedTriad():
                chord_type = "augmented"
            else:
                # Try to infer from common name
                common_name = chord_obj.commonName.lower()
                if 'minor' in common_name:
                    chord_type = "minor"
                elif 'dim' in common_name:
                    chord_type = "diminished"
                elif 'seventh' in common_name or '7' in common_name:
                    chord_type = "seventh"

            return {
                "root": root,
                "type": chord_type
            }

        except Exception as e:
            logger.warning(f"Chord analysis failed: {e}")
            return {
                "root": chord_obj.pitches[0].name if chord_obj.pitches else "C",
                "type": "major"
            }

    def _get_dynamics(self, element) -> Optional[str]:
        """
        Extract dynamic marking from note/chord.

        Args:
            element: music21 note or chord

        Returns:
            Dynamic marking string (pp, p, mf, f, ff, etc.) or None
        """
        try:
            if hasattr(element, 'volume') and element.volume.velocity:
                velocity = element.volume.velocity
                # Map velocity to dynamics
                if velocity < 20:
                    return "pp"
                elif velocity < 40:
                    return "p"
                elif velocity < 60:
                    return "mp"
                elif velocity < 80:
                    return "mf"
                elif velocity < 100:
                    return "f"
                else:
                    return "ff"
        except Exception:
            pass

        return None

    def _get_articulation(self, element) -> Optional[str]:
        """
        Extract articulation marking from note/chord.

        Args:
            element: music21 note or chord

        Returns:
            Articulation type or None
        """
        try:
            if hasattr(element, 'articulations') and element.articulations:
                artic = element.articulations[0]
                return type(artic).__name__.lower()
        except Exception:
            pass

        return None


# Factory function
def create_parser() -> MusicXMLParser:
    """
    Create and return a MusicXML parser instance.

    Returns:
        MusicXMLParser instance
    """
    return MusicXMLParser()
