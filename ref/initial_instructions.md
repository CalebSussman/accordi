initial_instructions.md
# INITIAL INSTRUCTIONS FOR AKKORDIO DEVELOPMENT

## START HERE
1. Read `coding_guidelines.md` FIRST - MANDATORY
2. Read `app_requirements.md` for complete specifications
3. Create session log in `session_logs/YYYYMMDD_Session.md`
4. Begin implementation

## PROJECT INITIALIZATION

### Step 1: Create Directory Structure
```
akkordio/
  backend/
    main.py                       # FastAPI application entry point
    omr.py                        # Audiveris OMR integration
    parser.py                     # MusicXML to MIDI conversion
    treble_mapping.py            # Right-hand button mapping logic
    bass_mapping.py              # Left-hand button mapping logic
    models.py                    # Pydantic models for API
    layouts/
      treble/
        c_system_5row_standard.json
        c_system_4row_standard.json
        c_system_3row_standard.json
        b_system_5row_standard.json
        b_system_4row_standard.json
        b_system_3row_standard.json
      bass/
        stradella_120_standard.json
        stradella_96_standard.json
        stradella_72_standard.json
        freebass_c_system.json
        freebass_b_system.json
        converter_c_system.json
    uploads/                     # Temporary upload storage
    processed/                   # Processed files storage
    requirements.txt            # Python dependencies
    .env.example               # Environment variables template

  frontend/
    index.html                  # Main application page
    css/
      main.css                 # Primary styles
      accordion.css            # Accordion-specific styles
      responsive.css           # Mobile/iPad optimizations
    js/
      app.js                   # Main application controller
      api.js                   # Backend API communication
      accordion_svg.js         # SVG keyboard rendering
      treble_view.js          # Treble animation controller
      bass_view.js            # Bass animation controller
      midi_player.js          # MIDI playback engine
      utils.js                # Utility functions
    assets/
      icons/                  # UI icons
      samples/                # Sample files

  test_data/
    sample_scores/            # Test PDF files
    expected_outputs/         # Expected JSON outputs

  session_logs/              # Development session logs

  docs/
    API.md                   # API documentation
    DEPLOYMENT.md           # Deployment instructions
    TROUBLESHOOTING.md      # Common issues and solutions

  .gitignore
  README.md
  LICENSE
  package.json              # For any frontend dependencies
```

### Step 2: Backend Foundation

#### 2.1 Create `backend/requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
music21==9.1.0
midiutil==1.2.1
pydantic==2.5.0
python-dotenv==1.0.0
aiofiles==23.2.1
Pillow==10.1.0
numpy==1.24.3
```

#### 2.2 Create `backend/main.py`:
- FastAPI application with CORS properly configured
- Health check endpoint: `GET /health`
- Upload endpoint: `POST /upload`
- Process endpoint: `POST /process`
- Get results endpoint: `GET /results/{job_id}`
- Static file serving for processed files
- WebSocket endpoint for real-time progress updates

#### 2.3 Create `backend/models.py`:
- Pydantic models for:
  - UploadResponse
  - ProcessRequest
  - ProcessResponse
  - TrebleEvent
  - BassEvent
  - MappingResult
  - ErrorResponse

### Step 3: Layout Files

#### 3.1 Create `backend/layouts/treble/c_system_5row_standard.json`:
Complete C-system layout with:
- Proper MIDI note mappings
- Row/column coordinates
- Enharmonic equivalents
- Metadata about the layout

#### 3.2 Create `backend/layouts/bass/stradella_120_standard.json`:
Complete Stradella bass layout with:
- Circle of fifths arrangement
- Root notes row
- Counter-bass row
- Major, minor, seventh, diminished chord rows
- Proper MIDI mappings for each button

### Step 4: Frontend Foundation

#### 4.1 Create `frontend/index.html`:
- Responsive layout with:
  - Header with app title and controls
  - PDF upload area (drag-and-drop enabled)
  - Split view for treble and bass keyboards
  - Playback controls (play, pause, tempo)
  - Settings panel (layout selection)
  - Status/progress indicators
- Touch-optimized for iPad
- Proper meta tags for PWA capability

#### 4.2 Create `frontend/css/main.css`:
- CSS custom properties for theming
- Flexbox/Grid layouts
- Touch-friendly button sizes (min 44x44px)
- Smooth animations
- Responsive breakpoints

#### 4.3 Create `frontend/js/app.js`:
- Main application initialization
- Event handling
- State management
- Coordination between modules

### Step 5: Core Functionality Implementation Order

1. **Phase 1: Basic Infrastructure**
   - Set up FastAPI server with CORS
   - Create file upload handling
   - Implement basic frontend with upload

2. **Phase 2: OMR Integration**
   - Integrate Audiveris CLI calls
   - Handle PDF to MusicXML conversion
   - Error handling for failed conversions

3. **Phase 3: Music Processing**
   - Parse MusicXML with music21
   - Extract treble and bass events
   - Convert to MIDI

4. **Phase 4: Mapping Logic**
   - Implement treble mapping algorithm
   - Implement bass mapping algorithm
   - Load and parse JSON layouts

5. **Phase 5: Visualization**
   - Generate SVG keyboards dynamically
   - Implement button highlighting
   - Add animation system

6. **Phase 6: Playback**
   - Integrate MIDI playback
   - Synchronize animations
   - Add playback controls

7. **Phase 7: Polish**
   - Optimize performance
   - Add error recovery
   - Improve UX

### Step 6: Testing Strategy

1. **Unit Tests:**
   - Mapping algorithms
   - Parser functions
   - Layout loading

2. **Integration Tests:**
   - File upload flow
   - OMR processing
   - Complete pipeline

3. **Frontend Tests:**
   - Browser compatibility
   - Touch interactions
   - Responsive design

4. **Performance Tests:**
   - Large PDF handling
   - Animation smoothness
   - Memory usage

### Step 7: Deployment Preparation

#### 7.1 GitHub Pages (Frontend):
- Build process for assets
- Configure CNAME if custom domain
- Update API endpoints for production

#### 7.2 Render.com (Backend):
- Create render.yaml configuration
- Set environment variables
- Configure build and start commands
- Set up persistent disk for uploads

## CRITICAL REMINDERS

1. **Every coding session MUST:**
   - Start by reading coding_guidelines.md
   - Create/update session log
   - Test changes before committing
   - Document any deviations

2. **Never implement:**
   - Database functionality (not in requirements)
   - User authentication (not in requirements)
   - Layout editor (marked as future feature)
   - Video export (marked as future feature)

3. **Always ensure:**
   - iPad Safari compatibility
   - Free, open-source dependencies only
   - Modular, extensible architecture
   - Complete, runnable code (no stubs)

## GETTING STARTED COMMANDS
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend setup
cd frontend
# If using any npm packages:
npm install
# Otherwise, just open index.html in browser

# Run tests
python -m pytest backend/tests/
```

## FIRST TASK

Begin by creating the complete directory structure and the following foundational files:
1. backend/main.py (working FastAPI server)
2. backend/requirements.txt
3. frontend/index.html (basic working interface)
4. frontend/css/main.css
5. .gitignore
6. README.md

Remember: Check /coding_guidelines.md and create your session log first!

