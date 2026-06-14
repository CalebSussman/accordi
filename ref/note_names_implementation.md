# Note Names Implementation Plan

**Created:** 2024-12-20
**Status:** In Progress
**Goal:** Display note names (e.g., "C4", "D#5") above each note in the rendered score

## Problem Statement

OSMD (OpenSheetMusicDisplay) does not natively support displaying text labels above notes. We need to implement a custom solution that:
1. Extracts note pitch information from OSMD's internal data structures
2. Positions text labels above each note head in the SVG rendering
3. Allows toggling the display on/off via the View controls panel
4. Updates when zoom or spacing changes (since positions change)

## Technical Approach

### Strategy: SVG Manipulation with OSMD Internal API

We'll use OSMD's `GraphicalMusicSheet` API to access rendered note positions and pitch data, then add SVG text elements.

**Why this approach:**
- Direct access to note positions (no DOM traversal needed)
- Accurate pitch information from source data
- Clean separation of concerns (rendering layer)
- Easy to toggle and re-render

## Implementation Steps

### 1. Create Note Name Renderer Module (`js/note_names.js`)

**Responsibilities:**
- Convert OSMD note data to note name strings
- Create and position SVG text elements
- Manage lifecycle (add/remove labels)
- Handle coordinate transformations

**Key Functions:**
```javascript
class NoteNameRenderer {
  constructor(osmdInstance)
  getNoteNameFromPitch(halfTone, octave, accidental)
  renderNoteNames()
  clearNoteNames()
  updatePositions()
}
```

### 2. Pitch to Note Name Conversion

**Lookup Table:**
```
0: C, 1: C#/Db, 2: D, 3: D#/Eb, 4: E, 5: F,
6: F#/Gb, 7: G, 8: G#/Ab, 9: A, 10: A#/Bb, 11: B
```

**Format:** `[NoteName][Accidental][Octave]` (e.g., "C#4", "Bb3")

**Edge Cases:**
- Handle enharmonic equivalents (prefer sharps over flats for now)
- Handle octave shifts for different clefs
- Handle grace notes vs regular notes

### 3. SVG Text Element Creation

**Positioning:**
- Get note's `PositionAndShape.RelativePosition` from OSMD
- Apply offset: Y-position - 15-20px (above note head)
- Convert OSMD units to SVG pixels using zoom factor

**Styling:**
```css
.note-name-label {
  fill: var(--gold-primary);
  font-size: 9px;
  font-family: system-ui, sans-serif;
  font-weight: 500;
  text-anchor: middle;
  pointer-events: none;
}
```

### 4. Integration with Score Controls

**Modify `score_controls.js`:**
- Import `NoteNameRenderer`
- Instantiate renderer on OSMD initialization
- Call `renderNoteNames()` or `clearNoteNames()` in `applyNoteNames()`
- Re-render after zoom/spacing changes

### 5. Lifecycle Management

**When to render:**
- After initial OSMD render
- After toggle on
- After zoom change
- After spacing change

**When to clear:**
- Before re-render
- After toggle off
- Before score unload

## Data Flow

```
User clicks "Note Names" toggle
  → applyNoteNames() called
    → If enabled: noteNameRenderer.renderNoteNames()
      → Iterate through OSMD.GraphicalMusicSheet.MusicPages
        → For each staff, measure, voice entry, note:
          → Get pitch data (halfTone, octave, accidental)
          → Get position (x, y)
          → Create SVG <text> element
          → Append to SVG container
    → If disabled: noteNameRenderer.clearNoteNames()
      → Remove all stored text elements
```

## OSMD API Reference

**Key Objects:**
```javascript
osmd.GraphicalMusicSheet.MusicPages[pageIndex]
  .MusicSystems[systemIndex]
  .StaffLines[staffIndex]
  .Measures[measureIndex]
  .staffEntries[entryIndex]
  .graphicalVoiceEntries[voiceIndex]
  .notes[noteIndex]
```

**Note Properties:**
```javascript
graphicalNote.sourceNote.Pitch
  .FundamentalNote  // 0-11 (C to B)
  .Octave           // e.g., 4 for middle C
  .Accidental       // -2=bb, -1=b, 0=natural, 1=#, 2=##

graphicalNote.PositionAndShape.RelativePosition
  .x  // Horizontal position
  .y  // Vertical position
```

## Testing Plan

1. **Basic Display:**
   - Load a simple score (e.g., C major scale)
   - Toggle note names on
   - Verify all notes have labels
   - Verify labels are positioned correctly above notes

2. **Accidentals:**
   - Load a score with sharps and flats
   - Verify correct note names (C#, Bb, etc.)

3. **Multiple Staves:**
   - Load a piano score (treble + bass clef)
   - Verify both staves show note names
   - Verify octave numbers are correct for each clef

4. **Zoom & Spacing:**
   - Enable note names
   - Zoom in/out
   - Adjust spacing
   - Verify labels stay positioned correctly

5. **Toggle Performance:**
   - Toggle on/off multiple times
   - Verify no memory leaks (labels are properly removed)
   - Verify no duplicate labels

6. **Persistence:**
   - Enable note names
   - Reload page
   - Verify setting is remembered and labels appear

## Known Limitations

1. **Performance:** Large scores (>200 notes) may have slight lag when toggling
2. **Collision Detection:** Labels may overlap with staff lines or other notation
3. **Chord Handling:** Stacked notes in chords may have overlapping labels
4. **Grace Notes:** May need special positioning logic

## Future Enhancements (Phase 6+)

- Collision detection and automatic label repositioning
- Configurable label format (solfège, scientific pitch notation, etc.)
- Color coding by note class or scale degree
- Label size scaling with zoom level
- Support for microtonal accidentals

## Files Modified

- **New:** `js/note_names.js` - Main renderer class
- **Modified:** `js/score_controls.js` - Integration with toggle control
- **Modified:** `css/score.css` - Styling for note labels (optional, can use inline SVG styles)

## Dependencies

- **OSMD v1.8.6+** (already in use)
- No additional libraries required

---

**Implementation Start:** 2024-12-20
**Estimated Completion:** Same day
**Priority:** High (User-facing feature)
