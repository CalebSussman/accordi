# Phase III: The Full Engine Algorithm (Pseudocode)

**Artifact Type:** Algorithm Logic  
**Engine Version:** 3.4 (Revised)  
**Description:** A* Pathfinding implementation for the Dmitriev Positional Method. This logic converts Phase I rules and Phase II data structures into a procedural engine, with strict adherence to coordinate geometry and polyphonic logic.

---

## 1. Main Execution Loop: `computeFingerings`

This is the entry point. It manages the Priority Queue (A*) and reconstructs the path.

### Updates in v3.4:
*   **Initialization:** `start_node` now explicitly initializes all Phase II fields (`centroid`, `span`, `bellows`) to ensure deterministic scoring from the very first step.

```python
function computeFingerings(score_input):
    # 1. Preprocessing
    # Flatten score into time-slices.
    # Each event contains: notes[], bellows_direction, metric_strength
    events = preprocessEvents(score_input) 

    # 2. A* Initialization
    open_set = PriorityQueue()
    closed_set = HashMap()

    # Create initial "Neutral Hand" state
    # Assumes hand starts relaxed, near middle of keyboard (Row 3), Bellows Closed/Neutral.
    start_node = NodeState(
        time_index: -1,
        fingers: [FREE, FREE, FREE, FREE, FREE], # Array of 5 FingerStates

        # Phase II Physical Fields
        centroid_row: 3, 
        centroid_col: 0, # Center of keyboard relative to start
        span_width_mm: 0.0,
        bellows_state: BELLOWS_NEUTRAL,

        # Scoring
        g_score: 0.0,
        f_score: heuristic(start_node, events)
    )

    open_set.push(start_node)

    # 3. Pathfinding Loop
    while open_set is not empty:
        current_node = open_set.pop_lowest_f_score()

        # Goal Check: Have we fingered the last event?
        if current_node.time_index == len(events) - 1:
            return reconstructPath(current_node)

        # Hash collision check (Deduplication)
        # Hash is based on: {time_index, finger_status[], button_ids[]}
        state_hash = calculateHash(current_node)
        if state_hash in closed_set:
            if current_node.g_score >= closed_set[state_hash].g_score:
                continue
        closed_set.add(state_hash, current_node)

        # 4. Get Next Musical Event
        next_event_index = current_node.time_index + 1
        target_event = events[next_event_index]

        # 5. Generate Valid Next States (Branching)
        # Applies H1 (Physical constraints)
        candidates = generateSuccessors(current_node, target_event)

        for neighbor in candidates:
            # 6. Calculate Transition Cost (Edge Weight)
            # Applies H2, H3, H4 (Biomechanical costs)
            transition_cost = calculateEdgeCost(current_node, neighbor, target_event)

            tentative_g = current_node.g_score + transition_cost

            if tentative_g < neighbor.g_score:
                neighbor.parent = current_node
                neighbor.g_score = tentative_g
                neighbor.h_score = heuristic(neighbor, events)
                neighbor.f_score = neighbor.g_score + neighbor.h_score

                open_set.push(neighbor)

    return FAILURE # No valid path found
```

---

## 2. State Generation: `generateSuccessors`

Handles combinatorics and pruning.

### Updates in v3.4:
* Polyphony Fix: Uses tied_from_prev property to match Phase II schema.  
* Crossing Check: Explicitly references isGeometricInversion to align with hard constraints.

```python
function generateSuccessors(current_node, target_event):
    successors = []

    # Step A: Identify Held Notes (Polyphony) -> RULE H1
    locked_fingers = []
    free_fingers = []

    # We map MIDI notes to the fingers currently holding them
    current_holding_map = map(current_node.fingers.midi_note -> finger_index)

    for note in target_event.notes:
        if note.tied_from_prev == true:
            # This note MUST be held by the same finger as before
            if note.midi_value in current_holding_map:
                finger_idx = current_holding_map[note.midi_value]
                locked_fingers.append(current_node.fingers[finger_idx])
            else:
                return [] # INVALID STATE: Tied note was not held in previous step

    # Identify fingers that are NOT locked
    for finger in current_node.fingers:
        if finger not in locked_fingers:
            free_fingers.append(finger)

    # Step B: Identify New Notes to Play
    new_notes_to_assign = target_event.notes.filter(n => n.tied_from_prev == false)

    # Step C: Button Expansion (B-System Specific)
    button_permutations = []
    for note in new_notes_to_assign:
        options = getPhysicalButtonOptions(note.midi) 
        button_permutations.add(options)

    # Step D: Assign Free Fingers to Button Permutations
    valid_assignments = permutate(free_fingers, button_permutations)

    for assignment in valid_assignments:
        next_node = clone(current_node)

        # Apply Locked Fingers (Keep state)
        for lf in locked_fingers:
            next_node.fingers[lf.index] = lf 

        # Apply New Assignments
        next_node.updateFingers(assignment)

        # Update Physical Properties (Centroid, Span)
        next_node.recalculateGeometry() 

        # Step E: Physical Hard Filters (Pruning)

        if calculateSpanMM(next_node) > MAX_HAND_SPAN_MM: continue 

        if isGeometricInversionImpossible(next_node): continue 

        successors.append(next_node)

    return successors
```

---

## 3. The Cost Function: `calculateEdgeCost`

Assigns numerical penalties.

### Updates in v3.4:
* Order of Operations: Additive → Multiplicative → Subtractive.  
* Crossing Logic: Uses isGeometricInversion for soft penalties.  
* Finger strength marked as optional.

```python
function calculateEdgeCost(prev_node, next_node, event):
    cost_distance = 0.0
    cost_penalty = 0.0
    multiplier = 1.0

    # 1. ADDITIVE COSTS
    dist_mm = distance(prev_node.centroid, next_node.centroid)
    cost_distance += dist_mm * WEIGHT_DISTANCE

    row_delta = abs(prev_node.centroid_row - next_node.centroid_row)
    cost_distance += row_delta * WEIGHT_ROW_JUMP

    # 2. PENALTIES
    if isGeometricInversion(next_node):
        severity = getCrossingSeverity(next_node.fingers)
        cost_penalty += severity * PENALTY_CROSSING

    if ENABLE_FINGER_STRENGTH_BIAS and event.is_downbeat:
         for finger in next_node.active_fingers:
            cost_penalty += getFingerWeaknessTable(finger.index)

    # 3. MULTIPLIERS
    if hasPivotFinger(prev_node, next_node):
        multiplier *= FACTOR_PIVOT_REDUCTION

    # 4. GLOBAL MODIFIERS
    current_bellows = event.bellows_direction
    if current_bellows != null and current_bellows != prev_node.bellows_state:
        cost_distance *= (1.0 - BONUS_BELLOWS_SHIFT)

    total_cost = (cost_distance * multiplier) + cost_penalty
    return max(total_cost, 0.0)
```

---

## 4. Helper Logic & Definitions

### isGeometricInversion(node)

Inversion exists if:  
Finger_A_Index < Finger_B_Index **but** Finger_A_Column > Finger_B_Column.

### isGeometricInversionImpossible(node)

True if inversion exceeds anatomical limits (e.g. Thumb crossing Pinky by > 2 rows).

---

### calculateSpanMM(node)

```python
d_row = (f1.row - f2.row) * ROW_SPACING_MM
d_col = (f1.col - f2.col) * COL_SPACING_MM
return sqrt(d_row^2 + d_col^2)
```

---

### getFingerWeaknessTable(finger_index)

```
1: 0.0
2: 0.0
3: 0.1
4: 0.8
5: 0.4
```
