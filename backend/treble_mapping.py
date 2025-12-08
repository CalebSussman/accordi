"""
Akkordio Backend - Treble Mapping

This module maps musical notes from parsed scores to treble (right-hand)
accordion button positions. Works with any chromatic layout (C-system, B-system).
"""

from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TrebleMapper:
    """
    Maps musical notes to treble accordion button positions.

    Handles:
    - Single notes
    - Chords (multiple simultaneous notes)
    - Optimal fingering paths
    - Enharmonic equivalents
    """

    def __init__(self, layout: Dict):
        """
        Initialize treble mapper with a layout.

        Args:
            layout: Layout dictionary from layout_generator
        """
        self.layout = layout
        self.note_index = layout.get("noteIndex", {})
        self.buttons = layout.get("buttons", [])
        self.system = layout.get("system", "unknown")

        logger.info(f"Treble mapper initialized for {self.system}")

    def map_note(self, midi: int) -> List[Dict]:
        """
        Find all possible button positions for a MIDI note.

        Args:
            midi: MIDI note number

        Returns:
            List of possible button positions
        """
        midi_str = str(midi)

        if midi_str in self.note_index:
            positions = self.note_index[midi_str]
            logger.debug(f"MIDI {midi} found at {len(positions)} positions")
            return positions

        logger.warning(f"MIDI {midi} not found in layout")
        return []

    def select_optimal_position(
        self,
        positions: List[Dict],
        previous_position: Optional[Dict] = None,
        next_midi: Optional[int] = None
    ) -> Dict:
        """
        Select optimal button position from multiple options.

        Strategy:
        1. If no previous position, prefer middle rows
        2. Minimize hand movement from previous position
        3. Consider upcoming notes for smoother path

        Args:
            positions: List of possible positions
            previous_position: Previously selected position
            next_midi: Next note's MIDI number (for lookahead)

        Returns:
            Selected optimal position
        """
        if not positions:
            raise ValueError("No positions available")

        if len(positions) == 1:
            return positions[0]

        # No context - prefer middle rows
        if previous_position is None:
            middle_row = self.layout.get("rows", 5) // 2
            positions_sorted = sorted(
                positions,
                key=lambda p: abs(p["row"] - middle_row)
            )
            return positions_sorted[0]

        # Minimize distance from previous position
        def distance(pos: Dict) -> float:
            """Calculate distance from previous position."""
            row_diff = pos["row"] - previous_position["row"]
            col_diff = pos["column"] - previous_position["column"]
            return (row_diff ** 2 + col_diff ** 2) ** 0.5

        # Sort by distance
        positions_sorted = sorted(positions, key=distance)

        # If we have lookahead, consider it
        if next_midi is not None:
            next_positions = self.map_note(next_midi)
            if next_positions:
                # Prefer position that's also close to next note
                def combined_score(pos: Dict) -> float:
                    current_dist = distance(pos)
                    # Average distance to all next positions
                    next_dists = [
                        ((pos["row"] - np["row"]) ** 2 +
                         (pos["column"] - np["column"]) ** 2) ** 0.5
                        for np in next_positions
                    ]
                    avg_next_dist = sum(next_dists) / len(next_dists)
                    return current_dist + 0.5 * avg_next_dist

                positions_sorted = sorted(positions, key=combined_score)

        return positions_sorted[0]

    def map_events(self, events: List[Dict]) -> List[Dict]:
        """
        Map a sequence of musical events to button positions.

        Args:
            events: List of treble event dictionaries from parser

        Returns:
            List of events with selected button positions
        """
        mapped_events = []
        previous_position = None

        for i, event in enumerate(events):
            midi = event.get("midi")

            if midi is None:
                logger.warning(f"Event missing MIDI: {event}")
                continue

            # Find all possible positions
            positions = self.map_note(midi)

            if not positions:
                logger.error(f"Cannot map MIDI {midi} - out of accordion range")
                continue

            # Get next MIDI for lookahead (if available)
            next_midi = None
            if i + 1 < len(events):
                next_midi = events[i + 1].get("midi")

            # Select optimal position
            selected = self.select_optimal_position(
                positions,
                previous_position,
                next_midi
            )

            # Create mapped event
            mapped_event = {
                **event,
                "button_positions": positions,
                "selected_position": selected
            }

            mapped_events.append(mapped_event)
            previous_position = selected

        logger.info(f"Mapped {len(mapped_events)}/{len(events)} events")
        return mapped_events

    def map_chord(self, midis: List[int]) -> List[Dict]:
        """
        Map a chord (multiple simultaneous notes) to button positions.

        Args:
            midis: List of MIDI note numbers in the chord

        Returns:
            List of button positions for all notes
        """
        chord_positions = []

        for midi in midis:
            positions = self.map_note(midi)
            if positions:
                # For chords, prefer positions in same general area
                # TODO: Implement chord-specific optimization
                chord_positions.append({
                    "midi": midi,
                    "positions": positions,
                    "selected": positions[0]  # Simple: use first option
                })
            else:
                logger.warning(f"Chord note MIDI {midi} not in range")

        return chord_positions

    def get_fingering_pattern(
        self,
        mapped_events: List[Dict]
    ) -> List[Dict]:
        """
        Analyze mapped events and suggest fingering patterns.

        This is a placeholder for future fingering optimization.
        Currently returns events as-is.

        Args:
            mapped_events: Events with selected positions

        Returns:
            Events with fingering suggestions
        """
        # TODO: Implement intelligent fingering patterns
        # - Detect scales, arpeggios
        # - Suggest finger numbers (1-5)
        # - Optimize for hand position changes

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
        mapped = sum(1 for e in mapped_events if "selected_position" in e)

        validation = {
            "total_events": total,
            "mapped_events": mapped,
            "unmapped_events": total - mapped,
            "success_rate": (mapped / total * 100) if total > 0 else 0,
            "valid": mapped == total
        }

        if not validation["valid"]:
            logger.warning(
                f"Mapping incomplete: {mapped}/{total} events mapped "
                f"({validation['success_rate']:.1f}%)"
            )

        return validation


def create_treble_mapper(layout: Dict) -> TrebleMapper:
    """
    Factory function to create a treble mapper.

    Args:
        layout: Layout dictionary from layout_generator

    Returns:
        TrebleMapper instance
    """
    return TrebleMapper(layout)
