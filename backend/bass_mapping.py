"""
Akkordio Backend - Bass Mapping

This module maps bass events to accordion bass buttons.
Handles two systems:
1. Free-Bass: Simple note-to-button mapping (like treble)
2. Stradella: Chord recognition and mapping to chord buttons
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BassMapper:
    """
    Maps bass musical events to accordion bass button positions.

    Handles both Free-Bass (chromatic) and Stradella (chord-based) systems.
    """

    def __init__(self, layout: Dict):
        """
        Initialize bass mapper with a layout.

        Args:
            layout: Layout dictionary from layout_generator
        """
        self.layout = layout
        self.system = layout.get("system", "unknown")
        self.note_index = layout.get("noteIndex", {})
        self.chord_index = layout.get("chordIndex", {})
        self.buttons = layout.get("buttons", [])

        logger.info(f"Bass mapper initialized for {self.system}")

    def map_single_note(self, midi: int) -> List[Dict]:
        """
        Map a single bass note to button positions.

        Works for:
        - Free-bass systems (direct chromatic mapping)
        - Stradella root/counter-bass notes

        Args:
            midi: MIDI note number

        Returns:
            List of possible button positions
        """
        midi_str = str(midi)

        if midi_str in self.note_index:
            positions = self.note_index[midi_str]
            logger.debug(f"Bass MIDI {midi} found at {len(positions)} positions")
            return positions

        logger.warning(f"Bass MIDI {midi} not found in layout")
        return []

    def map_chord_stradella(
        self,
        root: str,
        chord_type: str
    ) -> Optional[Dict]:
        """
        Map a chord to a Stradella button.

        Args:
            root: Chord root note (e.g., 'C', 'F#', 'Bb')
            chord_type: Chord type ('major', 'minor', 'seventh', 'diminished')

        Returns:
            Button position dict or None if not found
        """
        if self.system != "stradella":
            logger.warning("map_chord_stradella called on non-Stradella system")
            return None

        # Build chord key
        chord_key = f"{root}_{chord_type}"

        if chord_key in self.chord_index:
            position = self.chord_index[chord_key]
            logger.debug(f"Chord {chord_key} mapped to {position}")
            return position

        # Try enharmonic equivalents
        enharmonic_map = {
            'C#': 'Db', 'Db': 'C#',
            'D#': 'Eb', 'Eb': 'D#',
            'F#': 'Gb', 'Gb': 'F#',
            'G#': 'Ab', 'Ab': 'G#',
            'A#': 'Bb', 'Bb': 'A#'
        }

        if root in enharmonic_map:
            alt_root = enharmonic_map[root]
            alt_key = f"{alt_root}_{chord_type}"
            if alt_key in self.chord_index:
                position = self.chord_index[alt_key]
                logger.debug(f"Chord {chord_key} mapped via enharmonic {alt_key}")
                return position

        logger.warning(f"Chord {chord_key} not found in Stradella layout")
        return None

    def map_freebass_event(self, event: Dict) -> Dict:
        """
        Map a free-bass event (single note or chord).

        Free-bass systems are chromatic, so each note maps independently.

        Args:
            event: Bass event from parser

        Returns:
            Mapped event with button positions
        """
        event_type = event.get("event_type", "single_note")
        midis = event.get("midi", [])

        mapped_notes = []

        for midi in midis:
            positions = self.map_single_note(midi)

            if positions:
                mapped_notes.append({
                    "midi": midi,
                    "positions": positions,
                    "selected": positions[0]  # Use first position
                })
            else:
                logger.warning(f"Free-bass MIDI {midi} out of range")

        return {
            **event,
            "mapped_notes": mapped_notes,
            "mapping_complete": len(mapped_notes) == len(midis)
        }

    def map_stradella_event(self, event: Dict) -> Dict:
        """
        Map a Stradella event (chord or bass note).

        Args:
            event: Bass event from parser

        Returns:
            Mapped event with button position
        """
        event_type = event.get("event_type", "single_note")

        if event_type == "chord":
            # Map chord to chord button
            root = event.get("root")
            chord_type = event.get("chord_type", "major")

            if not root:
                logger.error(f"Chord event missing root: {event}")
                return {**event, "mapping_complete": False}

            button_position = self.map_chord_stradella(root, chord_type)

            if button_position:
                return {
                    **event,
                    "button_position": button_position,
                    "mapping_complete": True
                }
            else:
                return {
                    **event,
                    "mapping_complete": False,
                    "error": f"Chord {root} {chord_type} not available"
                }

        else:
            # Single note - map to root or counter-bass row
            midis = event.get("midi", [])

            if not midis:
                return {**event, "mapping_complete": False}

            # For single notes in Stradella, typically use root bass row
            # Find buttons in row 1 (root bass)
            root_buttons = [b for b in self.buttons if b["row"] == 1]

            # Try to match MIDI note
            midi = midis[0]
            matching = [b for b in root_buttons if b["midi"] == midi]

            if matching:
                return {
                    **event,
                    "button_position": {
                        "row": matching[0]["row"],
                        "column": matching[0]["column"]
                    },
                    "mapping_complete": True
                }
            else:
                logger.warning(f"Stradella single note MIDI {midi} not in root row")
                return {
                    **event,
                    "mapping_complete": False
                }

    def map_events(self, events: List[Dict]) -> List[Dict]:
        """
        Map a sequence of bass events to button positions.

        Args:
            events: List of bass event dictionaries from parser

        Returns:
            List of mapped events
        """
        mapped_events = []

        for event in events:
            if self.system == "stradella":
                mapped_event = self.map_stradella_event(event)
            else:
                # Free-bass systems
                mapped_event = self.map_freebass_event(event)

            mapped_events.append(mapped_event)

        # Count successful mappings
        successful = sum(
            1 for e in mapped_events
            if e.get("mapping_complete", False)
        )

        logger.info(
            f"Bass mapping: {successful}/{len(events)} events mapped "
            f"({successful/len(events)*100:.1f}%)"
        )

        return mapped_events

    def validate_mapping(self, mapped_events: List[Dict]) -> Dict:
        """
        Validate that all events were successfully mapped.

        Args:
            mapped_events: Mapped events

        Returns:
            Dictionary with validation results
        """
        total = len(mapped_events)
        mapped = sum(
            1 for e in mapped_events
            if e.get("mapping_complete", False)
        )

        validation = {
            "total_events": total,
            "mapped_events": mapped,
            "unmapped_events": total - mapped,
            "success_rate": (mapped / total * 100) if total > 0 else 0,
            "valid": mapped == total,
            "system": self.system
        }

        if not validation["valid"]:
            logger.warning(
                f"Bass mapping incomplete: {mapped}/{total} events "
                f"({validation['success_rate']:.1f}%)"
            )

        return validation

    def analyze_chord_usage(self, mapped_events: List[Dict]) -> Dict:
        """
        Analyze chord button usage in Stradella mappings.

        Args:
            mapped_events: Mapped Stradella events

        Returns:
            Dictionary with chord usage statistics
        """
        if self.system != "stradella":
            return {}

        chord_counts = {}
        total_chords = 0

        for event in mapped_events:
            if event.get("event_type") == "chord" and event.get("mapping_complete"):
                root = event.get("root", "Unknown")
                chord_type = event.get("chord_type", "major")
                key = f"{root} {chord_type}"

                chord_counts[key] = chord_counts.get(key, 0) + 1
                total_chords += 1

        # Sort by frequency
        sorted_chords = sorted(
            chord_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "total_chords": total_chords,
            "unique_chords": len(chord_counts),
            "most_common": sorted_chords[:10] if sorted_chords else [],
            "chord_counts": chord_counts
        }


def create_bass_mapper(layout: Dict) -> BassMapper:
    """
    Factory function to create a bass mapper.

    Args:
        layout: Layout dictionary from layout_generator

    Returns:
        BassMapper instance
    """
    return BassMapper(layout)
