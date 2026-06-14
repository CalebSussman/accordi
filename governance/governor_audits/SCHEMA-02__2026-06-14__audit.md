# SCHEMA-02 Audit

Date: 2026-06-14  
Role/work order: `SCHEMA-02`  
Work order: `SCHEMA-02-MUSICXML-MAPPING-CONTRACT`  
Execution mode: governor-executed inline role work; not an independent runtime sub-agent session.  
Verdict recommendation: PASS WITH CAVEATS

## 1. Task Summary

Defined the Phase 1 MusicXML upload/result contract and the deterministic B-system/120-bass Stradella mapping policy. The contract is written in `governance/musicxml_mapping_contract.md`.

## 2. Files Changed

- `governance/musicxml_mapping_contract.md`
- `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`

No backend implementation files were edited by this schema task.

## 3. Files Read

- `governance/source_truth.md`
- `governance/risk_register.md`
- `governance/governor_audits/DATA-01__2026-06-14__audit.md`
- `backend/models.py`
- `backend/main.py`
- `backend/parser.py`
- `backend/layout_generator.py`
- `backend/treble_mapping.py`
- `backend/bass_mapping.py`

## 4. Commands Run

```sh
sed -n '1,240p' governance/risk_register.md
sed -n '1,260p' governance/governor_audits/DATA-01__2026-06-14__audit.md
sed -n '1,260p' backend/models.py
sed -n '1,620p' backend/main.py
sed -n '1,320p' backend/treble_mapping.py
sed -n '1,380p' backend/bass_mapping.py
sed -n '620,760p' backend/main.py
```

## 5. Tests Run

No executable tests were run. This was contract/specification work.

## 6. Build Results

No build was run.

## 7. Data/Database Changes

None.

## 8. Deployment Changes

None.

## 9. Contract Decisions

- Phase 1 uses `POST /upload_musicxml`, `GET /musicxml/{job_id}`, and `GET /results/{job_id}`.
- `.mxl` uploads must normalize to plain MusicXML under `processed/{job_id}/{job_id}.musicxml`.
- `POST /upload_musicxml` must parse, map, save `result.json`, and return a real `results_url`.
- Default layouts:
  - treble: `b_system_5row`
  - bass: `stradella_120`
- Treble mapping must retain every source event and mark unmapped notes explicitly.
- Bass single notes map to Stradella root-bass row by pitch class, not exact octave.
- Bass chords map only to supported Stradella chord types: `major`, `minor`, `seventh`, `diminished`.
- Unsupported/ambiguous chords must remain in output with `mapping_complete: false` and an explanatory `error`.
- Validation must count source events, not only retained mapped events.

## 10. Known Blockers

- Existing backend code does not yet implement this contract.
- Existing unaccepted backend edits overlap with the contract but are not accepted by this audit.
- Treble B-system layout range must cover Bella Ciao MIDI `[57, 93]` or report explicit unmapped events.
- Bass chord classification inherits parser/music21 behavior; `WEB-03` must preserve transparent unmapped reasons.

## 11. Explicit Statement Of What Was Not Changed

- No backend source files were changed.
- No frontend files were changed.
- No PDF/OCR files were changed.
- No deployment or production state was changed.
- No mock data was created.

## 12. Handoff Recommendation

Proceed to `WEB-03` only after governor acceptance. `WEB-03` must implement `governance/musicxml_mapping_contract.md` and prove it with the Bella Ciao fixture through local API/TestClient verification.
