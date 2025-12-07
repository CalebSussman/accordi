# AKKORDIO APPLICATION REQUIREMENTS

## Executive Summary
Akkordio is a free, open-source web application that helps accordion players learn music by converting PDF scores into interactive accordion button fingerings with synchronized playback and visualization.

## Core Features

### 1. Score Processing Pipeline
**Input:** PDF music score
**Output:** Interactive accordion fingering visualization with MIDI playback

**Pipeline Steps:**
1. User uploads PDF score
2. Audiveris OMR converts PDF → MusicXML
3. Music21 processes MusicXML → structured music data
4. Extract separate treble (right-hand) and bass (left-hand) events
5. Map events to accordion button positions
6. Generate interactive visualization
7. Enable synchronized MIDI playback

### 2. Supported Accordion Systems

#### 2.1 Treble (Right Hand) Systems
- **C-System Chromatic Button Accordion**
  - 3-row variants (36-48 buttons)
  - 4-row variants (48-64 buttons)
  - 5-row variants (60-80 buttons)
  
- **B-System (Bayan) Chromatic Button Accordion**
  - 3-row variants
  - 4-row variants
  - 5-row variants

**Layout Configuration:** JSON files defining:
- Button positions (row, column)
- MIDI note mappings
- Enharmonic equivalents (C# = Db)
- Physical layout geometry

#### 2.2 Bass (Left Hand) Systems
- **Stradella Bass System**
  - 120-bass (6 rows × 20 columns)
  - 96-bass (6 rows × 16 columns)
  - 72-bass (6 rows × 12 columns)
  - 48-bass (6 rows × 8 columns)
  
  Rows (top to bottom):
  1. Counter-bass notes
  2. Root notes
  3. Major chords
  4. Minor chords
  5. Seventh chords
  6. Diminished chords

- **Free-Bass System**
  - Chromatic button layout
  - Mirror or non-mirror configuration
  - Single notes only (no chord buttons)

- **Converter System**
  - Switchable between Stradella and Free-bass
  - Uses both layout systems

### 3. Music Analysis Requirements

#### 3.1 Treble Event Extraction
Extract from MusicXML:
- Pitch (MIDI number)
- Note name (C, D, E, etc.)
- Octave
- Duration
- Measure number
- Beat position
- Articulation marks
- Dynamics

#### 3.2 Bass Event Extraction
Extract from MusicXML:
- Single notes vs. chords
- Chord identification:
  - Root note
  - Chord quality (major, minor, 7th, diminished)
- Bass note if different from root
- Duration and timing
- Measure and beat position

#### 3.3 Mapping Algorithm Requirements

**Treble Mapping:**
- Find all possible button positions for each note
- Prefer positions that minimize hand movement
- Consider previous and next notes for optimal path
- Support chords (multiple simultaneous notes)
- Handle enharmonic equivalents intelligently

**Bass Mapping:**
- Identify chord buttons for Stradella system
- Map single notes to appropriate row/button
- Use circle of fifths for Stradella root arrangement
- For free-bass, use chromatic layout mapping
- Suggest standard fingering patterns

### 4. Visualization Requirements

#### 4.1 SVG Keyboard Rendering
- **Treble Keyboard:**
  - Accurate button layout matching physical accordion
  - Different colors for note groups (C, C#, D, etc.)
  - Button labels (optional toggle)
  - Responsive sizing
  
- **Bass Keyboard:**
  - Stradella: Show all 6 rows with proper labels
  - Free-bass: Chromatic layout
  - Visual distinction between note/chord types
  - Circle of fifths visualization for Stradella

#### 4.2 Animation System
- Highlight buttons in real-time during playback
- Different colors for:
  - Current notes (bright)
  - Upcoming notes (dim preview)
  - Recently played (fade out)
- Smooth transitions between button presses
- Visual feedback for chord buttons

#### 4.3 Display Modes
- **Practice Mode:** Slow tempo with note labels
- **Performance Mode:** Full speed, minimal labels
- **Learning Mode:** Step-by-step progression
- **Analysis Mode:** Show all fingerings statically

### 5. Playback Requirements

#### 5.1 MIDI Playback Engine
- Use Tone.js or Web Audio API
- Accurate timing synchronization
- Variable tempo control (50% to 150%)
- Play/pause/stop controls
- Measure navigation (jump to measure)
- Loop sections for practice

#### 5.2 Audio Features
- Metronome (optional)
- Different instrument sounds
- Volume control
- Balance between hands

### 6. User Interface Requirements

#### 6.1 Layout
- **Header:** App title, main controls
- **Upload Area:** Drag-and-drop PDF upload
- **Control Panel:** Playback controls, settings
- **Main View:** Split or tabbed view for both keyboards
- **Info Panel:** Current measure, tempo, key signature

#### 6.2 Responsiveness
- Desktop: Full dual-keyboard view
- Tablet (iPad primary): Optimized touch controls
- Phone: Single keyboard view with toggle

#### 6.3 Touch Optimization
- Minimum touch target: 44×44px
- Swipe gestures for navigation
- Pinch-to-zoom on keyboards
- Touch-friendly sliders and controls

### 7. Technical Requirements

#### 7.1 Backend Stack
- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Music Processing:** music21
- **OMR:** Audiveris (via CLI)
- **MIDI:** midiutil
- **File Handling:** aiofiles
- **Validation:** Pydantic

#### 7.2 Frontend Stack
- **Core:** Vanilla JavaScript (ES6+)
- **Playback:** Tone.js or Web Audio API
- **Rendering:** SVG (no canvas)
- **Styling:** CSS3 with custom properties
- **No frameworks:** No React, Vue, Angular

#### 7.3 Data Formats
- **Layouts:** JSON
- **Music Data:** MusicXML (intermediate)
- **Audio:** MIDI
- **Communication:** REST API with JSON

#### 7.4 Performance Requirements
- PDF processing: < 30 seconds for 5-page score
- Initial load: < 3 seconds
- Animation: 60 FPS
- Memory: < 200MB for typical session

### 8. API Endpoints

#### 8.1 Core Endpoints
```
POST /upload
  - Accept PDF file
  - Return job ID
  
POST /process/{job_id}
  - Start OMR and processing
  - Return status

GET /status/{job_id}
  - Check processing status
  - Return progress percentage

GET /results/{job_id}
  - Get processed data
  - Return JSON with mappings

GET /midi/{job_id}
  - Download generated MIDI file

GET /musicxml/{job_id}
  - Download MusicXML file
```

#### 8.2 Configuration Endpoints
```
GET /layouts/treble
  - List available treble layouts

GET /layouts/bass
  - List available bass layouts

GET /layouts/treble/{layout_id}
  - Get specific treble layout

GET /layouts/bass/{layout_id}
  - Get specific bass layout
```

### 9. Error Handling

#### 9.1 OMR Errors
- Unreadable PDF
- Failed recognition
- Partial recognition
- Provide fallback options

#### 9.2 Mapping Errors
- Notes outside accordion range
- Unrecognized chords
- Ambiguous fingerings
- Provide manual override

#### 9.3 User Feedback
- Clear error messages
- Suggestions for resolution
- Progress indicators
- Success confirmations

### 10. Layout File Specification

#### 10.1 Treble Layout JSON Structure
```json
{
  "id": "c_system_5row",
  "name": "C-System 5-Row Chromatic",
  "system": "C",
  "rows": 5,
  "columns": 12,
  "startNote": "C3",
  "metadata": {
    "description": "Standard C-system layout",
    "totalButtons": 60,
    "range": "C3-C7"
  },
  "buttons": [
    {
      "row": 0,
      "column": 0,
      "note": "C3",
      "midi": 48,
      "enharmonic": ["B#2"],
      "color": "white"
    }
  ],
  "geometry": {
    "buttonRadius": 8,
    "rowOffset": 15,
    "columnOffset": 18,
    "stagger": true
  }
}
```

#### 10.2 Bass Layout JSON Structure
```json
{
  "id": "stradella_120",
  "name": "120-Bass Stradella System",
  "system": "stradella",
  "rows": 6,
  "columns": 20,
  "metadata": {
    "description": "Standard 120-bass Stradella",
    "chordRows": 4,
    "noteRows": 2
  },
  "buttons": [
    {
      "row": 0,
      "column": 0,
      "type": "counter-bass",
      "note": "Ab",
      "midi": 32,
      "label": "Ab"
    },
    {
      "row": 2,
      "column": 0,
      "type": "major-chord",
      "root": "Ab",
      "notes": ["Ab", "C", "Eb"],
      "midi": [56, 60, 63],
      "label": "AbM"
    }
  ],
  "circleOfFifths": {
    "order": ["Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B"],
    "startColumn": 4
  }
}
```

### 11. Security Requirements

#### 11.1 File Upload Security
- Maximum file size: 10MB
- Accepted formats: PDF only
- Virus scanning (if available)
- Sandboxed processing

#### 11.2 Input Validation
- Sanitize all user inputs
- Validate JSON structures
- Prevent path traversal
- Rate limiting on uploads

#### 11.3 CORS Configuration
- Whitelist allowed origins
- Proper headers for preflight
- Credentials handling

### 12. Deployment Requirements

#### 12.1 Frontend (GitHub Pages)
- Static file hosting
- Custom domain support
- HTTPS enforcement
- CDN distribution

#### 12.2 Backend (Render.com)
- Docker container deployment
- Environment variables for configuration
- Persistent storage for processed files
- Auto-scaling capabilities

#### 12.3 Monitoring
- Error logging
- Performance metrics
- Uptime monitoring
- Usage analytics (privacy-respecting)

### 13. Future Features (NOT for initial implementation)

These features should be considered in the architecture but NOT implemented:

1. **Layout Editor**
   - Visual drag-and-drop button arrangement
   - Custom layout creation
   - Layout sharing community

2. **Advanced Features**
   - Bellows direction indicators
   - Fingering optimization AI
   - Score following with highlighting
   - Video export of animations

3. **Social Features**
   - User accounts
   - Saved scores library
   - Sharing and collaboration
   - Community layouts

4. **Educational Features**
   - Practice tracking
   - Progress analytics
   - Tutorial system
   - Exercises generator

### 14. Constraints

#### 14.1 Technical Constraints
- No proprietary software dependencies
- No paid APIs or services
- Must work offline after initial load
- No database requirement

#### 14.2 Legal Constraints
- MIT License for codebase
- Respect music copyright
- GDPR compliance for any data
- No tracking without consent

#### 14.3 Design Constraints
- Accessibility WCAG 2.1 AA minimum
- International support (Unicode)
- No external font dependencies
- Progressive enhancement approach

### 15. Success Criteria

The application is considered complete when:

1. **Functional Requirements Met:**
   - PDF upload works reliably
   - OMR processing succeeds on standard scores
   - Mapping produces accurate fingerings
   - Visualization clearly shows button positions
   - Playback synchronizes with animation

2. **Performance Requirements Met:**
   - Loads in under 3 seconds
   - Processes typical scores in under 30 seconds
   - Animations run at 60 FPS
   - Works smoothly on iPad

3. **Quality Requirements Met:**
   - No critical bugs
   - Error handling for edge cases
   - Clear user feedback
   - Responsive on all target devices

4. **Documentation Complete:**
   - User guide
   - API documentation
   - Deployment instructions
   - Troubleshooting guide

## Appendix A: Sample Use Cases

### Use Case 1: Student Learning a New Piece
1. Student uploads PDF of accordion score
2. System processes and shows fingering
3. Student plays along at reduced tempo
4. Student gradually increases tempo
5. Student masters the piece

### Use Case 2: Teacher Preparing Materials
1. Teacher uploads standard piano score
2. System converts to accordion fingering
3. Teacher adjusts suggested fingerings
4. Teacher exports for student use
5. Students practice with consistent fingering

### Use Case 3: Professional Quick Reference
1. Professional uploads complex score
2. System analyzes difficult passages
3. Professional reviews fingering options
4. Professional chooses optimal path
5. Professional performs with confidence

## Appendix B: Technical Glossary

- **OMR:** Optical Music Recognition
- **MusicXML:** Standard music notation format
- **MIDI:** Musical Instrument Digital Interface
- **Stradella:** Standard accordion bass system
- **Free-bass:** Chromatic bass system
- **Chromatic:** All 12 semitones available
- **Circle of Fifths:** Musical relationship pattern
- **Enharmonic:** Same pitch, different notation