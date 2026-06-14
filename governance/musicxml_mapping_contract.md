# MusicXML Mapping Contract

Date: 2026-06-14  
Owner: `SCHEMA-02`  
Status: Accepted for Phase 1 implementation after governor audit

## Scope

This contract defines Phase 1 behavior for `.mxl`, `.musicxml`, and `.xml` upload-to-results flow. It explicitly excludes PDF upload, OEMER, Audiveris, Cloud Run, deployment, and frontend source/deploy reconciliation.

Primary fixture:

- `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`

Baseline instrument:

- Treble: B-system chromatic button accordion, 5-row dynamic layout.
- Bass: 120-bass Stradella dynamic layout.

## Endpoints

### `POST /upload_musicxml`

Accepts multipart form field:

- `file`: `.mxl`, `.musicxml`, or `.xml`

Required behavior:

1. Validate extension and max size.
2. Generate `job_id`.
3. Create `processed/{job_id}/`.
4. Normalize input to plain MusicXML at `processed/{job_id}/{job_id}.musicxml`.
5. Parse MusicXML into treble and bass source events.
6. Generate B-system treble and 120-bass Stradella layouts.
7. Map source events to layout buttons.
8. Save `processed/{job_id}/result.json`.
9. Store job status in memory as `completed` or `failed`.
10. Return response containing:

```json
{
  "success": true,
  "job_id": "uuid",
  "filename": "Bella_Ciao_-_La_Casa_de_Papel.mxl",
  "size": 12345,
  "status": "completed",
  "musicxml_url": "/musicxml/{job_id}",
  "results_url": "/results/{job_id}",
  "validation": {
    "treble": {},
    "bass": {}
  },
  "message": "MusicXML mapped successfully"
}
```

Failure behavior:

- Invalid extension: HTTP 400.
- Invalid `.mxl` archive or no score XML: HTTP 400.
- Parse/mapping failure caused by input: HTTP 400 if attributable to user file.
- Unexpected internal failure: HTTP 500, with job status `failed` when a job exists.
- Never return mock `results_url`.

### `GET /musicxml/{job_id}`

Required behavior:

- Return normalized plain MusicXML from `processed/{job_id}/{job_id}.musicxml`.
- Return HTTP 404 if the job or file does not exist.
- Content type: `application/vnd.recordare.musicxml+xml`.

### `GET /results/{job_id}`

Required behavior:

- Return real `processed/{job_id}/result.json`.
- Return HTTP 404 if job/file does not exist.
- Return HTTP 400 if job exists but is not complete.

Top-level response shape:

```json
{
  "job_id": "uuid",
  "treble_events": [],
  "bass_events": [],
  "metadata": {},
  "treble_layout_id": "b_system_5row",
  "bass_layout_id": "stradella_120",
  "treble_layout": {},
  "bass_layout": {},
  "validation": {
    "treble": {},
    "bass": {}
  }
}
```

## Normalized MusicXML Rules

- `.mxl` must be opened as ZIP.
- Use `META-INF/container.xml` if available to locate rootfile.
- If no usable container rootfile exists, fall back to first non-`META-INF` `.xml` entry.
- Write the selected XML bytes to `processed/{job_id}/{job_id}.musicxml`.
- Do not store or expose the original uploaded archive unless future work explicitly requires it.

## Treble Mapping Contract

Source:

- Use parser-identified treble part.
- For Bella Ciao fixture, DATA-01 observed:
  - treble events: `489`
  - MIDI range: `[57, 93]`

Layout:

- Default layout ID: `b_system_5row`.
- Layout must dynamically cover the source MIDI range for Phase 1. If the preset cannot cover `[57, 93]`, implementation must either:
  - expand the preset dynamically, or
  - produce explicit unmapped events and fail validation.

Event fields:

```json
{
  "measure": 1,
  "beat": 1.0,
  "duration": 0.5,
  "midi": 69,
  "note": "A4",
  "octave": 4,
  "dynamics": null,
  "articulation": null,
  "button_positions": [{"row": 0, "column": 0}],
  "selected_position": {"row": 0, "column": 0},
  "mapping_complete": true,
  "error": null
}
```

Rules:

- Every source treble event must appear in `treble_events`.
- Never silently drop an event.
- If MIDI is outside layout range, include event with:
  - `button_positions: []`
  - `selected_position: null`
  - `mapping_complete: false`
  - `error` explaining the unmapped reason.
- If multiple positions exist, choose deterministically. Initial policy: prefer middle rows for first note, then minimum row/column distance from prior selected position.

## Bass Mapping Contract

Source:

- Use parser-identified bass part.
- For Bella Ciao fixture, DATA-01 observed:
  - bass events: `514`
  - MIDI range: `[28, 62]`
  - event types: `236` single notes, `278` chords
  - source is piano-style bass clef, not Stradella-native.

Layout:

- Default layout ID: `stradella_120`.
- 120-bass Stradella layout has:
  - row 0: counter-bass
  - row 1: root bass
  - row 2: major chord
  - row 3: minor chord
  - row 4: dominant seventh chord
  - row 5: diminished chord

### Single Bass Notes

Rules:

- Map piano-style single bass notes to Stradella root-bass row by pitch class, not exact octave.
- Example: `E3` MIDI 52 maps to the `E` root bass button even if the layout stores `E2` or another canonical bass octave.
- If multiple root buttons with the same pitch class exist because the 120-bass layout repeats circle-of-fifths positions, choose deterministically by layout order unless a later ergonomics policy overrides it.
- Returned `button_position` must include enough UI/debug data:

```json
{
  "row": 1,
  "column": 8,
  "midi": 40,
  "note": "E",
  "label": "E",
  "type": "root"
}
```

### Bass Chords

Rules:

- Use parser-provided `root` and `chord_type` when `chord_type` is supported.
- Supported Stradella chord types:
  - `major` -> row 2
  - `minor` -> row 3
  - `seventh` -> row 4
  - `diminished` -> row 5
- Enharmonic roots must normalize where the layout uses the equivalent spelling.
- Dyads may map if parser confidently classifies them into a supported type. Example from DATA-01: `[G#3, B3]` parsed as `G# minor`; it may map to the `G# minor` button if present.
- Unsupported or ambiguous chord types must remain present with:
  - `mapping_complete: false`
  - `button_position: null`
  - `chord_button: null`
  - `error` explaining unsupported chord type/root.
- Do not invent accordion chord buttons outside the generated Stradella layout.

Bass event fields:

```json
{
  "measure": 1,
  "beat": 1.5,
  "duration": 0.5,
  "event_type": "chord",
  "midi": [56, 59],
  "notes": ["G#3", "B3"],
  "chord_type": "minor",
  "root": "G#",
  "button_position": {"row": 3, "column": 8},
  "chord_button": {"row": 3, "column": 8},
  "mapping_complete": true,
  "error": null
}
```

## Validation Contract

Each hand must include validation:

```json
{
  "source_events": 489,
  "mapped_events": 489,
  "unmapped_events": 0,
  "success_rate": 100.0,
  "valid": true,
  "system": "b-system",
  "unmapped_by_reason": {},
  "midi_range": [57, 93]
}
```

Requirements:

- `source_events` must equal parser source event count before mapping.
- `mapped_events + unmapped_events == source_events`.
- Validation must not be computed only from retained mapped events.
- Include `unmapped_by_reason` when unmapped events exist.
- Include layout IDs and systems in metadata or validation.

Bella Ciao target for Phase 1:

- Treble `source_events` must be `489`.
- Bass `source_events` must be `514`.
- A successful first pass should strive for 100% mapping. If less than 100%, it may still be acceptable only if all unmapped reasons are explicit and reviewed by `QA-05` and `GOV-00`.

## Backend Implementation Requirements For `WEB-03`

- Add or reuse a shared helper, e.g. `process_musicxml_file(job_id, musicxml_path, config)`, so upload and future PDF flow do not diverge.
- `POST /upload_musicxml` must call the shared parse/map/save path.
- Keep PDF/OCR out of Phase 1 changes except optionally calling the same shared helper after OMR in the future.
- Existing partial backend edits are not accepted merely because this contract references similar fields.

## Frontend Compatibility Requirements

The frontend keyboard renderer expects:

- `result.treble_layout`
- `result.bass_layout`
- `result.treble_events`
- `result.bass_events`
- treble events with `selected_position`
- bass events with `button_position`

If additional fields are added, they must not break these existing expectations.
