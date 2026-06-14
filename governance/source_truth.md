# Source Truth

Last updated: 2026-06-14  
Governor: `GOV-00`

## Canonical Repository State

- Repository: `CalebSussman/accordi`
- Canonical source worktree: `/Users/caleb/Documents/GitHub/akkordio-main`
- Canonical branch for source/docs/backend: `main`
- Deployment worktree: `/Users/caleb/Documents/GitHub/akkordio`
- Deployment branch: `gh-pages`

Current worktrees observed:

```text
/Users/caleb/Documents/GitHub/akkordio       124e218 [gh-pages]
/Users/caleb/Documents/GitHub/akkordio-main  ae4f899 [main]
```

## Canonical Project Tree

Canonical tree is the `main` worktree unless this file is updated by governor decision.

```text
.
./audiveris-service
./backend
./backend/processed
./backend/uploads
./frontend
./frontend/assets
./frontend/css
./frontend/js
./governance
./ref
./ref/TrebleRules
./session_logs
./test_data
./test_data/expected_outputs
./test_data/sample_scores
./tools
```

Local-only/non-source folders observed:

- `/Users/caleb/Documents/GitHub/akkordio-main/.venv` - local Python virtualenv, non-canonical, must not be committed.
- `/Users/caleb/Documents/GitHub/akkordio/backend/__pycache__` or `/Users/caleb/Documents/GitHub/akkordio-main/backend/__pycache__` - generated cache, non-canonical.

## Canonical Specs

The following are canonical until superseded by a governor decision:

- `/Users/caleb/Documents/GitHub/akkordio-main/governance/source_truth.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_work_orders.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/ref/application_requirements.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/ref/phase4_pdf_to_score_plan.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/ref/phase5_fingering_engine_plan.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/ref/dynamic_keyboards.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/ref/akkordio_dynamic_layouts.md`

If these specs conflict, this governance folder wins for current work sequencing and acceptance.

## Canonical Data Contracts

Phase 1 target:

- Input: user-provided `.mxl`, `.musicxml`, or `.xml` file.
- Primary fixture: `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`
- Baseline instrument:
  - Treble: B-system chromatic button accordion, 5-row default.
  - Bass: 120-bass Stradella.
- Backend must normalize `.mxl` to a retrievable MusicXML file.
- Backend must generate mapping results from MusicXML without PDF/OCR.

Expected API surface for Phase 1:

- `POST /upload_musicxml`
  - accepts `.mxl`, `.musicxml`, `.xml`
  - stores normalized MusicXML
  - parses score
  - maps treble and bass events
  - saves `processed/{job_id}/result.json`
  - returns `job_id`, `musicxml_url`, `results_url`, status, and validation summary
- `GET /musicxml/{job_id}`
  - returns normalized MusicXML for OSMD rendering
- `GET /results/{job_id}`
  - returns `MappingResult` with:
    - `job_id`
    - `treble_events`
    - `bass_events`
    - `metadata`
    - `treble_layout`
    - `bass_layout`
    - `validation`

No agent may present mocked `/results` data as proof of integration.

## Deployment Targets

- Frontend production: GitHub Pages at `https://calebsussman.github.io/accordi/`
- Backend production: Render at `https://akkordio.onrender.com`
- Render service name observed: `akkordio-backend`
- Google Cloud/Audiveris: historical/experimental OCR service. Not required for Phase 1.

## Known Duplicate Or Non-Canonical Folders

- `/Users/caleb/Documents/GitHub/akkordio` is the `gh-pages` deployment worktree. It contains root-level `index.html`, `js/`, `css/`, plus a `frontend/` subfolder. Treat it as deployment/frontend-only until a governor decision reconciles source/deploy flow.
- `/Users/caleb/Documents/GitHub/akkordio-main/frontend` is source-tree frontend from `main`, but may be stale relative to `gh-pages`. Do not assume it is production-current without diff/audit.
- `/Users/caleb/Documents/GitHub/akkordio/frontend` is a duplicate frontend subtree inside the `gh-pages` worktree. It is non-canonical unless specifically assigned.
- `audiveris-service/` and `cloudbuild.yaml` are PDF/OCR infrastructure artifacts. They are non-Phase-1 and must not be changed for MusicXML MVP work unless explicitly assigned.

Do not move or delete duplicate folders without explicit human authorization.

## Current Unaccepted Work

Before governance bootstrap, partial backend edits existed in `/Users/caleb/Documents/GitHub/akkordio-main`:

- `.gitignore`
- `backend/bass_mapping.py`
- `backend/layout_generator.py`
- `backend/models.py`
- `backend/treble_mapping.py`

These edits came from an interrupted implementation turn and are not accepted project state. They must be audited, repaired, or reverted only by explicit work order and governor acceptance.
