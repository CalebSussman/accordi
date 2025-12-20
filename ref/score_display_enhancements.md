# Score Display Enhancements Plan

## Goal
Enhance the score rendering UI with professional controls for playback, display customization, and future editing capabilities.

## Implementation Phases

### Phase 1: Menu Bar Enhancements (Immediate)

#### A. Playback Controls
**Location:** Top menu bar, left of settings button

**Controls:**
- Play/Pause button (▶️ / ⏸️)
- Stop button (⏹️)
- Tempo slider (50% - 200%)
- Current time / Total duration display

**Implementation:**
- Use OSMD's built-in PlaybackManager
- OSMD cursor follows playback automatically
- Audio synthesis via Web Audio API (OSMD built-in)

#### B. View Menu (Dropdown)
**Location:** Top menu bar, new button between "Upload" and "Settings"

**Options:**

1. **Score Appearance:**
   - Font: Sans-serif toggle (checkbox)
   - Note color selector (color picker)
   - Zoom level (50% - 200%)
   - Note spacing (compact / normal / wide)

2. **Annotations:** (toggles)
   - ☑️ Show note names (can implement now)
   - ☐ Show fingerings (Phase 5 - requires engine)
   - ☑️ Show chord symbols (OSMD has this)
   - ☑️ Show lyrics (OSMD has this)

3. **Display Mode:**
   - Page mode (default)
   - Continuous scroll mode

**Implementation:**
- OSMD `EngravingRules` for styling
- OSMD `RenderOptions` for display modes
- CSS for colors and fonts

#### C. Edit Menu (Future - Phase 5+)
**Location:** Top menu bar

**Features:**
- Click note to select
- Replace pitch (keyboard or input)
- Change duration
- Add/remove accidentals
- Undo/Redo stack
- Save modified MusicXML

**Implementation:**
- Requires MusicXML manipulation library (music21.js or custom)
- Re-render after each edit
- Complex - defer to Phase 6

---

### Phase 2: OSMD Configuration

#### Sans-Serif Font
**Current:** OSMD uses Bravura (serif music font)
**Goal:** Use sans-serif for text elements (titles, lyrics, note names)

**Implementation:**
```javascript
const osmd = new OpenSheetMusicDisplay('osmd-container', {
    backend: 'svg',
    drawTitle: true,
    drawComposer: true,
    drawPartNames: true,

    // Font settings
    defaultFontFamily: 'system-ui, -apple-system, sans-serif',

    // Display options
    autoResize: true,
    followCursor: true,
    cursorsOptions: {
        type: 3, // Standard cursor
        color: '#d4af37', // Gold
        alpha: 0.5
    }
});
```

#### Note Names Above Notes
**OSMD Option:** `drawNoteNames: true`

**Customization:**
```javascript
osmd.EngravingRules.RenderSingleHorizontalStaffline = false;
osmd.EngravingRules.RenderNoteNames = true;
```

#### Color Customization
**Method:** CSS styling of SVG elements

**Implementation:**
```css
/* Note heads */
#osmd-container .vf-notehead {
    fill: var(--note-color, #000000);
}

/* Stems and beams */
#osmd-container .vf-stem,
#osmd-container .vf-beam {
    stroke: var(--note-color, #000000);
}
```

#### Spacing and Width
**OSMD Options:**
```javascript
osmd.zoom = 1.0; // 0.5 to 2.0
osmd.EngravingRules.MinimumDistanceBetweenNotes = 3; // pixels
osmd.EngravingRules.MaximumDistanceBetweenNotes = 10;
```

---

### Phase 3: Playback Implementation

#### OSMD PlaybackManager
**Built-in features:**
- MIDI-like playback using Web Audio API
- Tempo control
- Cursor following
- Note highlighting

**Basic Setup:**
```javascript
import { PlaybackManager } from 'opensheetmusicdisplay';

const playbackManager = new PlaybackManager();
await playbackManager.initialize(osmd.Sheet);

// Play
playbackManager.play();

// Pause
playbackManager.pause();

// Stop
playbackManager.stop();

// Set tempo (0.5 = 50%, 2.0 = 200%)
playbackManager.setPlaybackSpeed(1.0);

// Listen to events
playbackManager.on('noteOn', (note) => {
    // Highlight corresponding accordion button
});
```

#### MIDI Export (Bonus)
**OSMD supports MIDI export:**
```javascript
const midiData = osmd.Sheet.exportMidi();
const blob = new Blob([midiData], { type: 'audio/midi' });
// Download or send to backend
```

---

### Phase 4: UI Layout

#### New Menu Structure

```
[Akkordio Logo]  [Upload] [View ▼] [Playback Controls] [Settings]
```

**Playback Controls Bar (when score loaded):**
```
[⏮️] [▶️/⏸️] [⏹️] [⏭️]  |  [Tempo: 100%] [🔊]  |  [0:45 / 3:22]
```

**View Dropdown:**
```
Appearance
  □ Sans-serif font
  Color: [🎨] #000000
  Zoom: [===|===] 100%
  Spacing: ○ Compact ● Normal ○ Wide

Annotations
  ☑ Note names
  ☐ Fingerings (disabled - requires Phase 5)
  ☑ Chord symbols
  ☑ Lyrics

Display
  ● Page view
  ○ Continuous scroll
```

---

## Implementation Order

### Sprint 1: Basic Playback (2-3 hours)
1. Add playback control buttons to navbar
2. Initialize OSMD PlaybackManager
3. Wire up play/pause/stop buttons
4. Add tempo slider
5. Add time display

### Sprint 2: View Menu (2-3 hours)
1. Create view dropdown menu
2. Add sans-serif font toggle
3. Implement note names toggle
4. Add zoom slider
5. Add color picker

### Sprint 3: Advanced Styling (1-2 hours)
1. CSS for note color customization
2. Spacing controls
3. Display mode toggle (page vs scroll)
4. Responsive adjustments

### Sprint 4: Polish (1 hour)
1. Keyboard shortcuts (Space = play/pause, etc.)
2. Smooth transitions
3. Loading states
4. Error handling
5. Save preferences to localStorage

---

## Files to Modify

**Frontend (gh-pages branch):**
- `index.html` - Add view menu, playback controls
- `css/score.css` - OSMD styling, color variables
- `js/app.js` - Playback manager, view controls
- `js/score_renderer.js` (NEW) - OSMD configuration

**Documentation:**
- `ref/phase5_fingering_engine_plan.md` - Add MIDI playback section
- `session_logs/20251220_Session.md` - Document enhancements

---

## Phase 5 Integration Points

### Fingering Display
**When fingering engine is ready:**
```javascript
// After fingering engine returns solution
const fingeringSolution = await API.generateFingerings(jobId);

// Render fingerings above notes
fingeringSolution.sequence.forEach(event => {
    event.assignments.forEach(assignment => {
        // Find corresponding note in OSMD
        const note = findNoteByMidi(assignment.midi_note, event.measure, event.beat);

        // Add text annotation above note
        addFingeringAnnotation(note, assignment.assigned_finger); // "1", "2", "3", "4", "5"
    });
});
```

### Accordion Button Highlighting During Playback
**Sync playback with keyboard visualization:**
```javascript
playbackManager.on('noteOn', (note) => {
    const midiNote = note.pitch;

    // Get fingering for this note
    const fingering = fingeringSolution.getFingeringForNote(midiNote);

    // Highlight button on accordion SVG
    highlightButton(fingering.button_location.row, fingering.button_location.column);
});
```

---

## Dependencies

**Already Available:**
- ✅ OpenSheetMusicDisplay (loaded via CDN)
- ✅ Web Audio API (browser built-in)
- ✅ CSS Variables (for theming)

**Need to Add:**
- None! (All features use existing libraries)

---

## Open Questions

1. **Edit Mode Complexity:** Score editing is very complex. Defer to Phase 6?
2. **MIDI Playback Quality:** Web Audio synthesis may sound robotic. Acceptable for MVP?
3. **Mobile Support:** Playback controls take up space. Collapse on mobile?
4. **Keyboard Shortcuts:** Standard music app shortcuts (Space, Left/Right arrows)?

---

**Created:** 2025-12-20
**Status:** Planning
**Estimated Implementation Time:** 6-8 hours
**Priority:** High - Core UX improvement
