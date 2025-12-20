# Phase 5: MusicXML to Fingering Instructions Plan

## Executive Summary

**Goal:** Enable users to upload MusicXML files and generate accordion fingering instructions based on the TrebleRules fingering algorithm.

**Status:** Phase 4 (PDF to MusicXML conversion) has failed due to infrastructure limitations. We are bypassing this by accepting MusicXML files directly, which the user will generate locally.

**Scope:** Implement the complete fingering engine that takes MusicXML input and produces optimal button positions with finger assignments (1-5) for the treble (right hand) keyboard using the Dmitriev Positional Method.

---

## Current State Assessment

### What Works ✅
- **Backend Infrastructure:** FastAPI server deployed on Render
- **MusicXML Parsing:** `parser.py` extracts musical events from MusicXML
- **Layout Generation:** `layout_generator.py` creates dynamic B-system/C-system keyboard layouts
- **Basic Treble Mapping:** `treble_mapping.py` maps MIDI notes to button positions (but doesn't assign fingers)
- **Frontend:** Upload interface exists, can display scores with OSMD

### What's Missing ❌
- **Fingering Algorithm:** No implementation of the TrebleRules A* pathfinding algorithm
- **Finger Assignment:** Current mapper only selects button positions, not which finger (1-5) to use
- **Cost Function:** No biomechanical cost calculation for hand movements
- **Polyphony Handling:** No locked finger tracking for held notes
- **Bellows State:** No bellows direction tracking/optimization
- **Frontend Visualization:** No way to display finger numbers on buttons
- **MusicXML Upload:** Currently expects PDF, need to accept .mxl/.musicxml files

### What Phase 4 Left Behind
- Audiveris Cloud Run service (deployed but not integrated)
- OEMER integration (abandoned due to memory limits)
- PDF upload functionality (not needed for Phase 5)

---

## Phase 5 Architecture

```
User Uploads MusicXML (.mxl)
    ↓
Backend: Parse MusicXML (parser.py) ✅ EXISTING
    ↓
Backend: Extract Treble Events ✅ EXISTING
    ↓
Backend: Generate Keyboard Layout ✅ EXISTING
    ↓
Backend: Run Fingering Algorithm ❌ NEW (Phase 5)
    ├── A* Pathfinding
    ├── Cost Function (H1-H5 rules)
    ├── Finger Assignment (1-5)
    └── Output: Fingering Sequence
    ↓
Backend: Return JSON Response ❌ NEW
    ├── Selected button positions
    ├── Assigned fingers (1-5)
    ├── Hand geometry metrics
    └── Metadata
    ↓
Frontend: Visualize Fingerings ❌ NEW
    ├── Highlight buttons on SVG keyboard
    ├── Show finger numbers
    ├── Sync with OSMD playback cursor
    └── Animate hand movements
```

---

## Implementation Plan

### Step 1: Data Structures (Backend)
**File:** `backend/fingering_models.py` (NEW)

Implement Phase II data structures from TrebleRules:

```python
@dataclass
class FingerState:
    """Represents the state of a single finger."""
    index: int  # 1-5 (thumb to pinky)
    status: str  # "free" | "pressing" | "locked_holding"
    current_button: Optional[ButtonPosition]
    frames_held: int

@dataclass
class HandGeometry:
    """Physical hand state metrics."""
    centroid_row: float
    centroid_col: float
    span_width_mm: float
    wrist_angle: float  # Diagnostic only

@dataclass
class NodeState:
    """A* search node representing a hand position."""
    id: str  # Hash of finger states
    parent_id: Optional[str]
    time_index: int
    fingers: List[FingerState]  # 5 fingers
    hand_geometry: HandGeometry
    g_score: float  # Accumulated cost
    h_score: float  # Heuristic cost
    f_score: float  # Total cost
    bellows_state: str  # "push" | "pull" | "neutral"

@dataclass
class FingeringAssignment:
    """Single note assignment in output."""
    midi_note: int
    assigned_finger: int  # 1-5
    button_location: ButtonPosition
    is_crossing: bool

@dataclass
class FingeringSolution:
    """Complete fingering solution."""
    total_cost: float
    algorithm: str  # "A_Star_Dmitriev"
    fingering_sequence: List[FingeringEvent]
```

**Dependencies:** None (dataclasses are standard library)

**Testing:** Unit tests for dataclass creation and validation

---

### Step 2: Fingering Engine Core (Backend)
**File:** `backend/fingering_engine.py` (NEW)

Implement the A* pathfinding algorithm from TrebleRules Phase III:

```python
class FingeringEngine:
    """
    Implements the Dmitriev Positional Method using A* pathfinding.

    Based on TrebleRules/3_Algorithmic pseudocode.md
    """

    def __init__(self, layout: Dict, rules: Dict):
        self.layout = layout
        self.rules = rules  # Load from TrebleRules/1_Rulebase.json

    def compute_fingerings(
        self,
        events: List[Dict],
        initial_bellows: str = "neutral"
    ) -> FingeringSolution:
        """
        Main entry point: compute optimal fingerings for a sequence.

        Args:
            events: Musical events from parser (treble only)
            initial_bellows: Starting bellows direction

        Returns:
            Complete fingering solution with finger assignments
        """
        # Implementation of Algorithm from pseudocode.md
        pass

    def _generate_successors(
        self,
        current_node: NodeState,
        target_event: Dict
    ) -> List[NodeState]:
        """Generate all valid next states (branching)."""
        pass

    def _calculate_edge_cost(
        self,
        prev_node: NodeState,
        next_node: NodeState,
        event: Dict
    ) -> float:
        """Calculate transition cost using H2-H5 rules."""
        pass

    def _apply_h1_constraints(self, node: NodeState) -> bool:
        """Check hard constraints (H1 layer rules)."""
        pass
```

**Key Features:**
- Priority queue for A* open set
- Hash-based closed set for visited states
- Heuristic function for lookahead
- State generation with finger locking for polyphony
- Cost calculation based on TrebleRules

**Dependencies:**
- `heapq` (priority queue)
- `fingering_models.py`

**Testing:**
- Simple melodic sequence (no polyphony)
- Chord with held notes
- Scale patterns
- Large jumps

---

### Step 3: Cost Function Implementation (Backend)
**File:** `backend/cost_calculator.py` (NEW)

Implement TrebleRules H2-H5 rules:

```python
class CostCalculator:
    """Calculates biomechanical costs for hand movements."""

    # Physical constants
    ROW_SPACING_MM = 15.0
    COL_SPACING_MM = 18.0
    MAX_HAND_SPAN_MM = 150.0

    # Weights and penalties
    WEIGHT_DISTANCE = 1.0
    WEIGHT_ROW_JUMP = 2.0
    PENALTY_CROSSING = 50.0
    BONUS_BELLOWS_SHIFT = 0.7

    def calculate_distance(
        self,
        prev_geo: HandGeometry,
        next_geo: HandGeometry
    ) -> float:
        """Euclidean distance between hand centroids."""
        pass

    def calculate_span_mm(self, node: NodeState) -> float:
        """Maximum distance between active fingers."""
        pass

    def is_geometric_inversion(self, node: NodeState) -> bool:
        """Check if fingers are crossing (H2_AVOID_AWKWARD_CROSSINGS)."""
        pass

    def get_finger_weakness_penalty(self, finger: int, is_strong_beat: bool) -> float:
        """Optional finger strength bias."""
        pass
```

**Dependencies:**
- `fingering_models.py`
- `math` (sqrt, etc.)

**Testing:**
- Distance calculations
- Span validation
- Crossing detection
- Cost accumulation

---

### Step 4: Update Backend API (Backend)
**File:** `backend/main.py` (MODIFY)

Add new endpoint for fingering generation:

```python
@app.post("/generate_fingerings")
async def generate_fingerings(
    file: UploadFile = File(...),
    system: str = Form("b-system"),
    rows: int = Form(5),
    columns: int = Form(12)
):
    """
    Generate fingering instructions from MusicXML file.

    Args:
        file: MusicXML file (.mxl or .musicxml)
        system: Accordion system ("b-system" or "c-system")
        rows: Number of keyboard rows
        columns: Number of keyboard columns

    Returns:
        JSON with fingering solution
    """
    # 1. Save uploaded MusicXML
    # 2. Parse with parser.py
    # 3. Generate layout with layout_generator.py
    # 4. Run fingering_engine.py
    # 5. Return solution as JSON
    pass
```

**Response Format:**
```json
{
  "success": true,
  "metadata": {
    "title": "Bella Ciao",
    "total_measures": 32,
    "tempo": 120
  },
  "layout": {
    "system": "b-system",
    "rows": 5,
    "columns": 12,
    "buttons": [...]
  },
  "fingering_solution": {
    "total_cost": 1234.56,
    "algorithm": "A_Star_Dmitriev",
    "sequence": [
      {
        "event_id": "uuid",
        "timestamp": 0.0,
        "measure": 1,
        "beat": 1.0,
        "bellows_state": "push",
        "assignments": [
          {
            "midi_note": 60,
            "note_name": "C4",
            "assigned_finger": 3,
            "button": {"row": 2, "column": 5},
            "is_crossing": false
          }
        ]
      }
    ]
  }
}
```

---

### Step 5: Frontend Upload Handler (Frontend)
**File:** `frontend/js/app.js` (MODIFY)

Update to accept MusicXML instead of PDF:

```javascript
// Change file input to accept .mxl and .musicxml
<input type="file" accept=".mxl,.musicxml" id="fileInput">

async function handleFileUpload(file) {
    if (!file.name.endsWith('.mxl') && !file.name.endsWith('.musicxml')) {
        showError('Please upload a MusicXML file (.mxl or .musicxml)');
        return;
    }

    // Get layout settings from UI
    const system = getSelectedSystem(); // "b-system" or "c-system"
    const rows = getSelectedRows(); // 3, 4, or 5
    const columns = getSelectedColumns(); // typically 11-12

    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('system', system);
    formData.append('rows', rows);
    formData.append('columns', columns);

    // Call backend
    const response = await fetch(API_URL + '/generate_fingerings', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (result.success) {
        // Render score with OSMD
        await renderScore(result.musicxml_url);

        // Visualize fingerings on keyboard
        await visualizeFingerings(result.fingering_solution, result.layout);
    }
}
```

---

### Step 6: Frontend Fingering Visualization (Frontend)
**File:** `frontend/js/fingering_visualizer.js` (NEW)

Animate fingerings synchronized with OSMD playback:

```javascript
class FingeringVisualizer {
    constructor(keyboardSvg, solution) {
        this.svg = keyboardSvg;
        this.solution = solution;
        this.currentIndex = 0;
    }

    /**
     * Highlight button and show finger number
     */
    highlightButton(assignment) {
        const button = this.findButtonElement(
            assignment.button.row,
            assignment.button.column
        );

        // Add gold glow
        button.classList.add('active-fingering');

        // Show finger number overlay
        const fingerLabel = document.createElementNS(SVG_NS, 'text');
        fingerLabel.textContent = assignment.assigned_finger;
        fingerLabel.setAttribute('class', 'finger-number');
        // Position on button center
        this.svg.appendChild(fingerLabel);
    }

    /**
     * Advance to next event (sync with MIDI playback)
     */
    nextEvent() {
        if (this.currentIndex >= this.solution.sequence.length) return;

        const event = this.solution.sequence[this.currentIndex];

        // Clear previous highlights
        this.clearHighlights();

        // Highlight all assignments for this event (handles chords)
        event.assignments.forEach(assignment => {
            this.highlightButton(assignment);
        });

        this.currentIndex++;
    }

    /**
     * Sync with OSMD cursor position
     */
    syncWithOSMD(osmd) {
        // Match current OSMD cursor position to event index
        const currentMeasure = osmd.cursor.iterator.currentMeasure;
        // Find matching event in solution
        // Update visualization
    }
}
```

**CSS Styling:**
```css
/* Active fingering highlight */
.active-fingering {
    fill: url(#goldGradient);
    filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.8));
    animation: goldPulse 0.3s ease-out;
}

/* Finger number label */
.finger-number {
    font-size: 20px;
    font-weight: bold;
    fill: white;
    text-anchor: middle;
    pointer-events: none;
}
```

---

### Step 7: Integration Testing

**Test Scenarios:**

1. **Simple Melody (No Chords)**
   - Input: "Mary Had a Little Lamb" MusicXML
   - Expected: Single-finger assignments, smooth transitions
   - Validate: No finger crossings, reasonable hand movements

2. **Scale Pattern**
   - Input: C major scale ascending/descending
   - Expected: Logical finger progression (avoid same finger on consecutive notes in legato)
   - Validate: H1_LEGATO_NO_REPEAT rule applied

3. **Chord with Held Notes**
   - Input: C major chord held while melody plays
   - Expected: Locked fingers tracked, remaining fingers free for melody
   - Validate: H1_POLY_LOCKED_FINGER rule applied

4. **Large Jump**
   - Input: Low C to high C octave jump
   - Expected: Position shift with central finger pivot
   - Validate: H4_CENTRAL_PIVOT_SHIFT preference

5. **Staccato Passage**
   - Input: Staccato notes with same finger hopping
   - Expected: H3_STACCATO_FINGER_HOP allows same finger
   - Validate: Hop distance penalty applied

**Success Criteria:**
- All test cases produce valid fingerings
- No hard constraint violations (H1)
- Cost function produces reasonable scores
- Frontend visualization shows correct finger numbers
- OSMD playback syncs with fingering highlights

---

## Implementation Order

### Week 1: Core Algorithm
1. Create `fingering_models.py` with data structures ✅
2. Load TrebleRules JSON into Python dictionaries ✅
3. Implement `FingeringEngine.compute_fingerings()` skeleton
4. Implement `_generate_successors()` with polyphony handling
5. Unit test: simple 3-note melody

### Week 2: Cost Function
6. Create `cost_calculator.py` with H2-H5 implementations
7. Integrate cost calculator into `_calculate_edge_cost()`
8. Test: verify costs match expected values for known scenarios
9. Tune weights/penalties based on test results

### Week 3: Backend Integration
10. Update `main.py` with `/generate_fingerings` endpoint
11. Wire up parser → layout generator → fingering engine
12. Test end-to-end: upload MusicXML, get fingering JSON
13. Deploy to Render, test production endpoint

### Week 4: Frontend Visualization
14. Create `fingering_visualizer.js`
15. Integrate with existing accordion SVG renderer
16. Add OSMD sync logic
17. Test with sample MusicXML files
18. Polish animations and styling

---

## File Structure After Phase 5

```
backend/
├── fingering_models.py      ← NEW (data structures)
├── fingering_engine.py       ← NEW (A* algorithm)
├── cost_calculator.py        ← NEW (H2-H5 rules)
├── main.py                   ← MODIFY (add endpoint)
├── parser.py                 ✅ EXISTING
├── layout_generator.py       ✅ EXISTING
├── treble_mapping.py         ← MODIFY (integrate engine)
└── rules/
    ├── rulebase.json         ← COPY from TrebleRules/1_Rulebase.json
    └── weights.json          ← NEW (tunable parameters)

frontend/
├── js/
│   ├── app.js                ← MODIFY (MusicXML upload)
│   ├── fingering_visualizer.js ← NEW (visualization)
│   └── api.js                ← MODIFY (new endpoint)
└── css/
    └── fingering.css         ← NEW (finger number styling)
```

---

## Dependencies to Add

**Backend:**
```txt
# No new dependencies needed!
# All required libraries already in requirements.txt:
# - music21 (MusicXML parsing)
# - pydantic (data validation)
# - fastapi (API)
```

**Frontend:**
```html
<!-- No new dependencies needed! -->
<!-- OSMD already loaded for score rendering -->
```

---

## Known Challenges & Mitigations

### Challenge 1: Algorithm Complexity
**Problem:** A* pathfinding can be slow for long pieces (100+ notes)
**Mitigation:**
- Implement beam search (limit branching factor)
- Add timeout with best-effort solution
- Cache computed paths for repeated sections

### Challenge 2: Rule Interpretation
**Problem:** TrebleRules pseudocode may have ambiguities
**Mitigation:**
- Start with simple test cases
- Iteratively refine based on musical common sense
- Document deviations from original rules

### Challenge 3: Frontend Performance
**Problem:** Rendering hundreds of finger numbers may be slow
**Mitigation:**
- Only render visible measures
- Use CSS transforms instead of re-rendering
- Debounce playback sync updates

### Challenge 4: Bellows State Tracking
**Problem:** MusicXML doesn't encode bellows direction
**Mitigation:**
- Start with neutral bellows assumption
- Add manual override in UI for advanced users
- Future: heuristic detection based on phrasing

---

## Success Metrics

Phase 5 is complete when:

- [x] User can upload MusicXML file
- [x] Backend generates fingering solution without errors
- [x] Fingering solution respects all H1 hard constraints
- [x] Cost function produces reasonable scores
- [x] Frontend displays finger numbers (1-5) on buttons
- [x] Visualization syncs with OSMD playback
- [x] At least 5 test pieces work correctly
- [x] Documentation written for fingering algorithm
- [x] Session log created for all changes

---

## What's NOT in Phase 5

**Defer to Future Phases:**
- Bass (left hand) fingering (Stradella/Free-bass)
- Bellows direction optimization (needs score annotation)
- Fingering pattern learning/personalization
- Export to annotated MusicXML with fingerings
- Multi-hand coordination (treble + bass sync)
- Manual fingering override/editing UI
- Fingering comparison (show alternative solutions)

---

## Deployment Plan

**Backend Deployment (Render):**
1. Commit all new Python files
2. Push to main branch (auto-deploys to Render)
3. Verify `/generate_fingerings` endpoint responds
4. Test with curl/Postman before frontend integration

**Frontend Deployment (GitHub Pages):**
1. Commit all new JS/CSS files
2. Test locally first
3. Push to gh-pages branch
4. Verify at https://calebsussman.github.io/accordi/

**Testing in Production:**
1. Upload "Bella Ciao.mxl" (from /ref)
2. Verify fingering generation completes
3. Check finger numbers display correctly
4. Test playback sync

---

## Documentation Deliverables

1. **FINGERING_ENGINE.md** - How the algorithm works
2. **API.md** - Updated with new endpoint
3. **SESSION_LOG.md** - All changes documented
4. **TESTING.md** - Test cases and results

---

## Next Steps After Phase 5

**Phase 6: Bass Fingering**
- Extend engine to handle Stradella chord buttons
- Implement bass-specific rules
- Coordinate treble + bass timing

**Phase 7: Advanced Features**
- Bellows optimization
- Fingering alternatives (show top 3 solutions)
- Export annotated MusicXML
- User preference learning

**Phase 8: Polish & Release**
- Performance optimization
- Comprehensive test suite
- User documentation
- Public beta launch

---

**Created:** 2025-12-20
**Status:** Planning Phase
**Priority:** Critical (core feature blocker)
**Estimated Effort:** 4 weeks
**Risk Level:** Medium (algorithm complexity, no GPU needed)
