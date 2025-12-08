"""
Akkordio Backend - Dynamic Layout Generator

This module generates accordion keyboard layouts dynamically based on:
- System type (C-system, B-system, Free-bass, Stradella)
- Number of rows and columns
- Starting MIDI note
- Chromatic intervals

No static JSON files needed - supports any accordion variant.
"""

from typing import List, Dict, Callable, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SystemType(str, Enum):
    """Accordion system types."""
    C_SYSTEM = "c-system"
    B_SYSTEM = "b-system"
    FREEBASS_C = "freebass-c"
    FREEBASS_B = "freebass-b"
    STRADELLA = "stradella"


# Pitch class to color mapping
PITCH_CLASS_COLORS = {
    0: "white",    # C
    1: "dark",     # C#/Db
    2: "blue",     # D
    3: "dark",     # D#/Eb
    4: "green",    # E
    5: "yellow",   # F
    6: "orange",   # F#/Gb
    7: "red",      # G
    8: "gray",     # G#/Ab
    9: "purple",   # A
    10: "purple",  # A#/Bb
    11: "teal"     # B
}

# MIDI note number to note name
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC_MAP = {
    'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb',
    'E': 'Fb', 'B': 'Cb', 'C': 'B#', 'F': 'E#'
}

# Circle of fifths sequence (starting from Ab)
CIRCLE_OF_FIFTHS = ['Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#']


def midi_to_note_name(midi: int) -> str:
    """
    Convert MIDI note number to note name with octave.

    Args:
        midi: MIDI note number (0-127)

    Returns:
        Note name with octave (e.g., 'C4', 'F#3')
    """
    octave = (midi // 12) - 1
    note = NOTE_NAMES[midi % 12]
    return f"{note}{octave}"


def get_pitch_class_color(note: str) -> str:
    """
    Get color for a note based on its pitch class.

    Args:
        note: Note name (e.g., 'C', 'F#', 'Bb')

    Returns:
        Color string
    """
    # Extract just the note name without octave
    note_base = note.rstrip('0123456789')

    # Get MIDI pitch class (0-11)
    try:
        pitch_class = NOTE_NAMES.index(note_base)
    except ValueError:
        # Try enharmonic equivalent
        for original, enharmonic in ENHARMONIC_MAP.items():
            if note_base == enharmonic:
                pitch_class = NOTE_NAMES.index(original)
                break
        else:
            pitch_class = 0  # Default to C

    return PITCH_CLASS_COLORS.get(pitch_class, "white")


def generate_chromatic_layout(
    system: str,
    rows: int,
    columns: int,
    start_midi: int,
    row_offsets: List[int],
    col_offset_func: Callable[[int], int],
    geometry: Optional[Dict] = None
) -> Dict:
    """
    Generate a chromatic button layout dynamically.

    Args:
        system: System type identifier (e.g., 'c-system', 'b-system')
        rows: Number of button rows
        columns: Number of button columns
        start_midi: Starting MIDI note number
        row_offsets: Semitone offsets for each row [0, +1, +2, ...]
        col_offset_func: Function that returns semitone offset for column index
        geometry: Optional geometry configuration

    Returns:
        Dictionary containing layout data
    """
    buttons = []
    note_index = {}

    for row in range(rows):
        for col in range(columns):
            # Calculate MIDI note
            midi = start_midi + row_offsets[row] + col_offset_func(col)

            # Convert to note name
            note = midi_to_note_name(midi)
            note_base = note.rstrip('0123456789')

            # Get enharmonic equivalents
            enharmonic = []
            if note_base in ENHARMONIC_MAP:
                enharmonic_name = ENHARMONIC_MAP[note_base]
                octave = note[-1]
                enharmonic.append(f"{enharmonic_name}{octave}")

            # Create button object
            button = {
                "row": row,
                "column": col,
                "note": note,
                "midi": midi,
                "enharmonic": enharmonic,
                "color": get_pitch_class_color(note_base),
                "type": "note"
            }

            buttons.append(button)

            # Build note index for quick lookup
            if str(midi) not in note_index:
                note_index[str(midi)] = []
            note_index[str(midi)].append({"row": row, "column": col})

    # Default geometry if not provided
    if geometry is None:
        geometry = {
            "buttonRadius": 8,
            "rowSpacing": 15,
            "columnSpacing": 18,
            "staggered": True,
            "staggerOffset": 9
        }

    return {
        "system": system,
        "rows": rows,
        "columns": columns,
        "startMidi": start_midi,
        "buttons": buttons,
        "noteIndex": note_index,
        "geometry": geometry
    }


def generate_c_system(rows: int, columns: int, start_midi: int) -> Dict:
    """
    Generate C-system chromatic layout.

    Row intervals: [0, +1, +2, +3, +4]
    Column offset: whole tone (+2 semitones)

    Args:
        rows: Number of rows (3, 4, or 5 typical)
        columns: Number of columns (11-13 typical)
        start_midi: Starting MIDI note (typically 48 for C3)

    Returns:
        Layout dictionary
    """
    row_offsets = [i for i in range(rows)]
    col_offset_func = lambda col: col * 2  # Whole tone

    return generate_chromatic_layout(
        system="c-system",
        rows=rows,
        columns=columns,
        start_midi=start_midi,
        row_offsets=row_offsets,
        col_offset_func=col_offset_func
    )


def generate_b_system(rows: int, columns: int, start_midi: int) -> Dict:
    """
    Generate B-system (Bayan) chromatic layout.

    Row intervals: [0, +1, +2, +3, +4] (same as C)
    Column offset: whole tone (+2 semitones)
    Starting note: B (one semitone lower than C-system)

    Args:
        rows: Number of rows (3, 4, or 5 typical)
        columns: Number of columns (11-13 typical)
        start_midi: Starting MIDI note (typically 47 for B2)

    Returns:
        Layout dictionary
    """
    row_offsets = [i for i in range(rows)]
    col_offset_func = lambda col: col * 2  # Whole tone

    return generate_chromatic_layout(
        system="b-system",
        rows=rows,
        columns=columns,
        start_midi=start_midi,
        row_offsets=row_offsets,
        col_offset_func=col_offset_func
    )


def generate_freebass(
    system: str,
    rows: int,
    columns: int,
    start_midi: int
) -> Dict:
    """
    Generate free-bass chromatic layout.

    Free-bass uses the same interval logic as treble systems,
    but in a lower register.

    Args:
        system: 'freebass-c' or 'freebass-b'
        rows: Number of rows
        columns: Number of columns
        start_midi: Starting MIDI note (typically 36 for C2 or 35 for B1)

    Returns:
        Layout dictionary
    """
    row_offsets = [i for i in range(rows)]
    col_offset_func = lambda col: col * 2  # Whole tone

    geometry = {
        "buttonRadius": 7,
        "rowSpacing": 14,
        "columnSpacing": 16,
        "staggered": True,
        "staggerOffset": 8
    }

    return generate_chromatic_layout(
        system=system,
        rows=rows,
        columns=columns,
        start_midi=start_midi,
        row_offsets=row_offsets,
        col_offset_func=col_offset_func,
        geometry=geometry
    )


def generate_stradella(
    columns: int,
    start_fifth_index: int = 4
) -> Dict:
    """
    Generate Stradella bass system layout.

    Stradella follows the circle of fifths horizontally,
    with 6 rows vertically:
    - Row 0: Counter-bass (major 3rd above root)
    - Row 1: Root bass
    - Row 2: Major chords
    - Row 3: Minor chords
    - Row 4: Dominant 7th chords
    - Row 5: Diminished chords

    Args:
        columns: Number of columns (typically 12-20)
        start_fifth_index: Index in circle of fifths to start (4 = C)

    Returns:
        Layout dictionary
    """
    buttons = []
    chord_index = {}
    rows = 6

    # Map circle of fifths notes to MIDI (root in octave 2)
    fifth_to_midi = {
        'Ab': 44, 'Eb': 39, 'Bb': 46, 'F': 41, 'C': 36, 'G': 43,
        'D': 38, 'A': 45, 'E': 40, 'B': 47, 'F#': 42, 'C#': 37,
        'G#': 44, 'D#': 39, 'A#': 46
    }

    for col in range(columns):
        # Get root note from circle of fifths
        fifth_idx = (start_fifth_index + col) % len(CIRCLE_OF_FIFTHS)
        root = CIRCLE_OF_FIFTHS[fifth_idx]
        root_midi = fifth_to_midi.get(root, 36)

        # Row 0: Counter-bass (major 3rd above root = +4 semitones)
        counterbass_midi = root_midi + 4
        buttons.append({
            "row": 0,
            "column": col,
            "type": "counter-bass",
            "note": midi_to_note_name(counterbass_midi),
            "midi": counterbass_midi,
            "label": root,
            "color": get_pitch_class_color(root)
        })

        # Row 1: Root bass
        buttons.append({
            "row": 1,
            "column": col,
            "type": "root",
            "note": root,
            "midi": root_midi,
            "label": root,
            "color": get_pitch_class_color(root)
        })

        # Row 2: Major chord
        buttons.append({
            "row": 2,
            "column": col,
            "type": "major",
            "note": root,
            "midi": root_midi,
            "label": root,
            "color": get_pitch_class_color(root)
        })
        chord_index[f"{root}_major"] = {"row": 2, "column": col}

        # Row 3: Minor chord
        buttons.append({
            "row": 3,
            "column": col,
            "type": "minor",
            "note": root,
            "midi": root_midi,
            "label": f"{root}m",
            "color": get_pitch_class_color(root)
        })
        chord_index[f"{root}_minor"] = {"row": 3, "column": col}

        # Row 4: Dominant 7th chord
        buttons.append({
            "row": 4,
            "column": col,
            "type": "seventh",
            "note": root,
            "midi": root_midi,
            "label": f"{root}7",
            "color": get_pitch_class_color(root)
        })
        chord_index[f"{root}_seventh"] = {"row": 4, "column": col}

        # Row 5: Diminished chord
        buttons.append({
            "row": 5,
            "column": col,
            "type": "diminished",
            "note": root,
            "midi": root_midi,
            "label": f"{root}dim",
            "color": get_pitch_class_color(root)
        })
        chord_index[f"{root}_diminished"] = {"row": 5, "column": col}

    geometry = {
        "buttonRadius": 6,
        "rowSpacing": 12,
        "columnSpacing": 14,
        "staggered": False
    }

    return {
        "system": "stradella",
        "rows": rows,
        "columns": columns,
        "buttons": buttons,
        "chordIndex": chord_index,
        "geometry": geometry,
        "circleOfFifths": CIRCLE_OF_FIFTHS[start_fifth_index:] + CIRCLE_OF_FIFTHS[:start_fifth_index]
    }


# Preset configurations for common accordions
PRESET_CONFIGS = {
    "c_system_5row": {
        "type": SystemType.C_SYSTEM,
        "rows": 5,
        "columns": 12,
        "start_midi": 48  # C3
    },
    "c_system_4row": {
        "type": SystemType.C_SYSTEM,
        "rows": 4,
        "columns": 12,
        "start_midi": 48
    },
    "c_system_3row": {
        "type": SystemType.C_SYSTEM,
        "rows": 3,
        "columns": 11,
        "start_midi": 48
    },
    "b_system_5row": {
        "type": SystemType.B_SYSTEM,
        "rows": 5,
        "columns": 12,
        "start_midi": 47  # B2
    },
    "b_system_4row": {
        "type": SystemType.B_SYSTEM,
        "rows": 4,
        "columns": 12,
        "start_midi": 47
    },
    "b_system_3row": {
        "type": SystemType.B_SYSTEM,
        "rows": 3,
        "columns": 11,
        "start_midi": 47
    },
    "freebass_c_5row": {
        "type": SystemType.FREEBASS_C,
        "rows": 5,
        "columns": 12,
        "start_midi": 36  # C2
    },
    "freebass_b_5row": {
        "type": SystemType.FREEBASS_B,
        "rows": 5,
        "columns": 12,
        "start_midi": 35  # B1
    },
    "stradella_120": {
        "type": SystemType.STRADELLA,
        "columns": 20,
        "start_fifth_index": 4  # Start at C
    },
    "stradella_96": {
        "type": SystemType.STRADELLA,
        "columns": 16,
        "start_fifth_index": 4
    },
    "stradella_72": {
        "type": SystemType.STRADELLA,
        "columns": 12,
        "start_fifth_index": 4
    },
    "stradella_48": {
        "type": SystemType.STRADELLA,
        "columns": 8,
        "start_fifth_index": 4
    }
}


def generate_layout(
    system_type: str,
    rows: Optional[int] = None,
    columns: Optional[int] = None,
    start_midi: Optional[int] = None,
    **kwargs
) -> Dict:
    """
    Main layout generator function.

    Args:
        system_type: Type of system ('c-system', 'b-system', 'freebass-c', etc.)
        rows: Number of rows (optional for presets)
        columns: Number of columns (optional for presets)
        start_midi: Starting MIDI note (optional for presets)
        **kwargs: Additional parameters

    Returns:
        Generated layout dictionary

    Raises:
        ValueError: If invalid system type or missing parameters
    """
    system_type = system_type.lower()

    if system_type == "c-system":
        if rows is None or columns is None or start_midi is None:
            raise ValueError("C-system requires rows, columns, and start_midi")
        return generate_c_system(rows, columns, start_midi)

    elif system_type == "b-system":
        if rows is None or columns is None or start_midi is None:
            raise ValueError("B-system requires rows, columns, and start_midi")
        return generate_b_system(rows, columns, start_midi)

    elif system_type in ["freebass-c", "freebass-b"]:
        if rows is None or columns is None or start_midi is None:
            raise ValueError("Free-bass requires rows, columns, and start_midi")
        return generate_freebass(system_type, rows, columns, start_midi)

    elif system_type == "stradella":
        if columns is None:
            raise ValueError("Stradella requires columns")
        start_fifth_index = kwargs.get('start_fifth_index', 4)
        return generate_stradella(columns, start_fifth_index)

    else:
        raise ValueError(f"Unknown system type: {system_type}")


def get_preset_layout(preset_name: str) -> Dict:
    """
    Get a layout from a preset configuration.

    Args:
        preset_name: Name of the preset (e.g., 'c_system_5row')

    Returns:
        Generated layout dictionary

    Raises:
        ValueError: If preset not found
    """
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"Unknown preset: {preset_name}")

    config = PRESET_CONFIGS[preset_name]
    system_type = config["type"]

    if system_type == SystemType.STRADELLA:
        return generate_stradella(
            columns=config["columns"],
            start_fifth_index=config.get("start_fifth_index", 4)
        )
    else:
        return generate_layout(
            system_type=system_type,
            rows=config.get("rows"),
            columns=config["columns"],
            start_midi=config["start_midi"]
        )
