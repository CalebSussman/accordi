# Governor Audit: WEB-03

Date: 2026-06-14  
Governor: `GOV-00`  
Audited role/work-order artifact: `WEB-03`  
Runtime QA sub-agent: `019ec3a9-0f22-7922-99d8-f44a624fc098`  
Work order: `WEB-03-BACKEND-MUSICXML-MAPPING`  
Verdict: PASS WITH CAVEATS

## Execution Provenance

The WEB-03 implementation was executed inline by the governor process before runtime sub-agent tooling was invoked. After the human corrected this process issue, runtime `QA-05` was spawned as sub-agent `019ec3a9-0f22-7922-99d8-f44a624fc098` and independently audited the backend behavior.

## Evidence Inspected

Files inspected:

- `governance/musicxml_mapping_contract.md`
- `governance/governor_audits/WEB-03__2026-06-14__audit.md`
- `governance/governor_audits/QA-05__2026-06-14__audit.md`
- `backend/main.py`
- `backend/models.py`
- `backend/parser.py`
- `backend/layout_generator.py`
- `backend/treble_mapping.py`
- `backend/bass_mapping.py`

Commands run by GOV-00:

```sh
git status --short --branch && git diff --stat && git diff --name-only
rg -n "upload_musicxml|process_musicxml_file|results_url|source_events|unmapped_by_reason|b_system_5row|stradella_120|button_position" backend/main.py backend/treble_mapping.py backend/bass_mapping.py backend/models.py backend/layout_generator.py
.venv/bin/python -m py_compile backend/main.py backend/models.py backend/parser.py backend/layout_generator.py backend/treble_mapping.py backend/bass_mapping.py
PYTHONPATH=backend .venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8766
HTTP upload/status/musicxml/results verification against /Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl
rm -rf processed uploads && git status --short --branch
```

Commands run by runtime QA-05 are recorded in `governance/governor_audits/QA-05__2026-06-14__audit.md`.

## Objective Findings

- Python compile check passed for the required backend files.
- `/upload_musicxml` accepts the Bella Ciao `.mxl`, normalizes it, maps it, and returns:
  - `job_id`
  - `musicxml_url`
  - `results_url`
  - validation summary
- `/status/{job_id}` returned completed status and 100 progress.
- `/musicxml/{job_id}` returned normalized MusicXML with content type `application/vnd.recordare.musicxml+xml` and 536714 bytes.
- `/results/{job_id}` returned real mapping data, not mock data.
- Result counts match DATA-01 fixture evidence:
  - treble events: 489
  - bass events: 514
- Result layout IDs match the accepted contract:
  - `b_system_5row`
  - `stradella_120`
- Validation counts match source counts:
  - treble `source_events`: 489
  - treble `mapped_events`: 489
  - bass `source_events`: 514
  - bass `mapped_events`: 514
- Representative bass conversion proof exists:
  - E3 maps by pitch class to E root bass button.
  - G# minor dyad maps to G# minor Stradella chord button.
- Missing results return HTTP 404.
- Invalid upload extension returns HTTP 400.
- Runtime root-level `processed/` and `uploads/` directories created during local proof were removed.

## Scope Compliance

Accepted scope:

- Backend MusicXML upload/result implementation.
- Backend layout/model/mapper repairs required for Phase 1.
- Governance audit documentation.

Forbidden scope respected:

- No frontend files were changed.
- No PDF/OCR, Audiveris, Cloud Run, Google Cloud, Render, GitHub Pages, deployment, database, or production credential changes were made.
- No fixture file was modified.
- No duplicate folders were moved or deleted.

## Caveats

- Acceptance is local backend-only. It does not prove frontend rendering, hosted Render behavior, GitHub Pages, PDF/OCR, Audiveris, or Google Cloud.
- FastAPI `TestClient` is unavailable because `httpx` is not installed in the virtualenv; real local HTTP proof was used instead.
- Backend runtime paths remain relative to the process working directory. Starting the app from repository root creates root-level `processed/` and `uploads/`; those artifacts were cleaned after verification, but the behavior should be reviewed before deployment hardening.
- The accepted backend diff includes some changes that existed before the WEB-03 work order (`.gitignore`, `backend/layout_generator.py`, `backend/models.py`). They are now accepted only because WEB-03 and QA-05 verified them as necessary for the Phase 1 contract.

## Governor Decision

PASS WITH CAVEATS. WEB-03 is accepted for local Phase 1 backend MusicXML upload-to-results behavior against the Bella Ciao fixture.

## Handoff

Do not deploy yet. Next valid step is either:

- `UI-04`: after governor names the canonical frontend source path, integrate frontend with real `/upload_musicxml`, `/musicxml/{job_id}`, and `/results/{job_id}`.
- Additional backend hardening work order: make runtime upload/processed paths stable relative to the backend module or configured app root.
