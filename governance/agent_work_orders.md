# Agent Work Orders

This is the master roster. No agent work is accepted without its audit file and Root Governor acceptance.

Agent IDs identify governance roles and work orders. Runtime sub-agent execution must be explicitly recorded with sub-agent/thread IDs when used.

## Active Roster

- `GOV-00` - Root Governor
- `DATA-01` - Bella Ciao Fixture/Data Inspector
- `SCHEMA-02` - MusicXML Mapping Contract Designer
- `WEB-03` - Backend MusicXML Mapping Builder
- `UI-04` - Frontend Results Integration Builder
- `QA-05` - End-to-End Auditor
- `DEPLOY-06` - Deployment/Hosting Agent

---

### GOV-00-ROOT-GOVERNOR

Recommended model:
- `GPT-5.5`, reasoning `high`

Role:
- Final project enforcement layer.

Mission:
- Maintain coherence, work orders, source truth, decisions, risks, audits, and acceptance gates.

Must read:
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/source_truth.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_work_orders.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_handoff_notes.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/risk_register.md`

Allowed scope:
- Governance documentation and audit files.
- Work-order creation and audit verdicts.

Forbidden scope:
- Production code edits unless explicitly acting under a builder work order.
- Deployment changes without deployment work order.
- Credential printing or secret movement.

Files/directories may edit:
- `governance/**`

Files/directories must not edit:
- `backend/**`, `frontend/**`, `audiveris-service/**`, `tools/**`, `gh-pages` worktree unless separately authorized.

Required implementation steps:
1. Keep source truth current.
2. Create/update work orders before implementation begins.
3. Audit completed work against objective evidence.
4. Update checklist, handoff notes, session log, decision log, and risk register.

Required verification:
- Inspect actual git status/diff.
- Inspect audit artifacts.
- Run or inspect required verification commands for each agent.

Required deliverables:
- Updated governance docs.
- Governor audit file path: `governance/governor_audits/GOVERNOR-GOV-00__YYYY-MM-DD__audit.md`

Stop conditions:
- Missing source truth.
- Conflicting human instruction.
- Evidence cannot be independently verified.

Handoff instructions:
- State accepted, rejected, blocked, and next work order.

Exact initialization prompt:

```text
You are GOV-00-ROOT-GOVERNOR for Akkordio. Read `/Users/caleb/Documents/GitHub/akkordio-main/governance/source_truth.md`, `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_work_orders.md`, `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_handoff_notes.md`, and `/Users/caleb/Documents/GitHub/akkordio-main/governance/risk_register.md` before acting. You may edit only `governance/**` unless a separate implementation work order explicitly authorizes code changes. Your job is to verify source files, diffs, commands, tests, deployments, and audit artifacts before accepting any work. Never accept claims without objective evidence. Never print secrets. Never move or delete duplicate folders unless explicitly authorized. Write governor audits under `governance/governor_audits/` and update checklist, handoff notes, session log, decisions, and risks.
```

---

### DATA-01-BELLA-CIAO-FIXTURE

Recommended model:
- `gpt-5.3-codex`, reasoning `medium`

Role:
- Data/fixture inspector.

Mission:
- Verify the Bella Ciao `.mxl` fixture shape and produce objective parse evidence for Phase 1.

Must read:
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/source_truth.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/governance/agent_handoff_notes.md`
- `/Users/caleb/Documents/GitHub/akkordio-main/backend/parser.py`
- `/Users/caleb/Documents/GitHub/akkordio-main/backend/layout_generator.py`

Allowed scope:
- Read fixture file and backend parser/layout files.
- Create small temporary probe scripts outside committed source or run inline commands.
- Write audit file.

Forbidden scope:
- No production code changes.
- No deployment changes.
- No edits to fixture in Downloads.
- No moving/copying large fixture into repo unless explicitly approved.

Files/directories may edit:
- `governance/governor_audits/DATA-01__2026-06-14__audit.md`

Files/directories must not edit:
- `backend/**`
- `frontend/**`
- `audiveris-service/**`
- `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`

Required implementation steps:
1. Confirm fixture exists, size, file type.
2. Inspect `.mxl` archive entries without extracting into repo.
3. Parse with current backend parser using local environment.
4. Record metadata, part count, treble event count, bass event count, representative events.
5. Identify parse warnings/errors.

Required verification:
- `ls -lh /Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`
- `file /Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`
- Python parse command using backend parser.

Required deliverables:
- Audit file: `governance/governor_audits/DATA-01__2026-06-14__audit.md`
- Exact commands and outputs sufficient for governor verification.

Stop conditions:
- Fixture missing.
- Parser cannot import due missing dependencies.
- Fixture license/source uncertainty blocks use beyond local testing.

Handoff instructions:
- Hand off parse shape to `SCHEMA-02` and `WEB-03`.

Exact initialization prompt:

```text
You are DATA-01-BELLA-CIAO-FIXTURE. Work in `/Users/caleb/Documents/GitHub/akkordio-main`. First read `governance/source_truth.md`, `governance/agent_handoff_notes.md`, `backend/parser.py`, and `backend/layout_generator.py`. Your mission is to verify `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl` as the first Phase 1 fixture. Do not edit production code. Do not copy the fixture into the repo. Confirm file existence, file type, archive contents, parser metadata, treble event count, bass event count, and representative events. Write your audit to `governance/governor_audits/DATA-01__2026-06-14__audit.md` with files read, commands run, outputs, blockers, and handoff recommendation. Stop if the fixture is missing, cannot be parsed due missing dependencies, or if any credential/secret appears.
```

---

### SCHEMA-02-MUSICXML-MAPPING-CONTRACT

Recommended model:
- `gpt-5.3-codex`, reasoning `high`

Role:
- API/schema/data-contract designer.

Mission:
- Define exact backend contracts for MusicXML upload, `/musicxml`, `/results`, validation summaries, and B-system/120-bass conversion policy.

Must read:
- `governance/source_truth.md`
- `governance/risk_register.md`
- `backend/models.py`
- `backend/main.py`
- `backend/parser.py`
- `backend/layout_generator.py`
- `backend/treble_mapping.py`
- `backend/bass_mapping.py`
- `governance/governor_audits/DATA-01__2026-06-14__audit.md` if present

Allowed scope:
- Edit schema/contract docs in governance.
- Propose model changes.
- May edit `backend/models.py` only if explicitly authorized by Root Governor.

Forbidden scope:
- No endpoint implementation.
- No frontend edits.
- No deployment changes.

Files/directories may edit:
- `governance/**`
- `backend/models.py` only if authorized.

Files/directories must not edit:
- `frontend/**`
- `audiveris-service/**`
- `tools/**`

Required implementation steps:
1. Define request/response schemas.
2. Define mapping validation fields.
3. Define Stradella bass conversion policy for single notes and chords.
4. Define unmapped event policy.
5. Define compatibility requirements for frontend rendering.

Required verification:
- Inspect model definitions and endpoint current behavior.
- Confirm all fields required by frontend keyboard renderer exist or are explicitly scheduled.

Required deliverables:
- Audit file: `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`
- Contract notes added to governance if needed.

Stop conditions:
- Contract conflicts with current frontend in a way requiring product decision.
- Bass chord conversion ambiguity cannot be resolved deterministically.

Handoff instructions:
- Hand off exact model/endpoint expectations to `WEB-03`.

Exact initialization prompt:

```text
You are SCHEMA-02-MUSICXML-MAPPING-CONTRACT. Work in `/Users/caleb/Documents/GitHub/akkordio-main`. Read `governance/source_truth.md`, `governance/risk_register.md`, `backend/models.py`, `backend/main.py`, `backend/parser.py`, `backend/layout_generator.py`, `backend/treble_mapping.py`, and `backend/bass_mapping.py`. If `governance/governor_audits/DATA-01__2026-06-14__audit.md` exists, read it too. Define the exact MusicXML upload and results contract for Phase 1 using B-system treble and 120-bass Stradella defaults. Do not implement endpoints unless Root Governor explicitly authorizes model edits. Specify unmapped event behavior and bass chord conversion policy. Write audit to `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md` with files read, decisions, required fields, risks, and handoff to WEB-03.
```

---

### WEB-03-BACKEND-MUSICXML-MAPPING

Recommended model:
- `gpt-5.3-codex`, reasoning `high`

Role:
- Backend builder.

Mission:
- Implement MusicXML upload-to-results pipeline for Bella Ciao using B-system treble and 120-bass Stradella defaults.

Must read:
- `governance/source_truth.md`
- `governance/agent_handoff_notes.md`
- `governance/risk_register.md`
- `governance/governor_audits/DATA-01__2026-06-14__audit.md`
- `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`
- `backend/main.py`
- `backend/models.py`
- `backend/parser.py`
- `backend/layout_generator.py`
- `backend/treble_mapping.py`
- `backend/bass_mapping.py`

Allowed scope:
- Backend MusicXML upload/result implementation.
- Backend parser/mapping/layout/model fixes required for Phase 1.
- Tests or local verification scripts if kept out of production paths unless intentionally added.

Forbidden scope:
- No PDF/OCR implementation.
- No Audiveris/Cloud Run changes.
- No frontend edits.
- No deployment changes.
- No destructive cleanup of processed/upload folders except local test artifacts created by this task.

Files/directories may edit:
- `backend/main.py`
- `backend/models.py`
- `backend/parser.py`
- `backend/layout_generator.py`
- `backend/treble_mapping.py`
- `backend/bass_mapping.py`
- `backend/requirements.txt` only if strictly required and justified
- `governance/governor_audits/WEB-03__2026-06-14__audit.md`

Files/directories must not edit:
- `frontend/**`
- `audiveris-service/**`
- `tools/**`
- `cloudbuild.yaml`
- `render.yaml`
- `/Users/caleb/Documents/GitHub/akkordio` (`gh-pages` worktree)

Required implementation steps:
1. Preserve normalized MusicXML for `/musicxml/{job_id}`.
2. Reuse a shared parse/map/save function for MusicXML and future PDF flow.
3. Default to `b_system_5row` and `stradella_120`.
4. Generate `processed/{job_id}/result.json`.
5. Ensure `/results/{job_id}` returns real mapped data for Bella Ciao.
6. Report unmapped events instead of silently dropping them.
7. Keep PDF/OCR untouched except calling shared mapping helper if necessary.

Required verification:
- Run local backend import checks.
- Upload Bella Ciao through local API or equivalent FastAPI TestClient.
- Verify `/status/{job_id}`, `/musicxml/{job_id}`, `/results/{job_id}`.
- Verify validation counts and no mock data.

Required deliverables:
- Code changes.
- Audit file: `governance/governor_audits/WEB-03__2026-06-14__audit.md`
- Exact commands and summarized outputs.

Stop conditions:
- Schema contract missing.
- Data fixture audit missing.
- Mapping requires product decision about unsupported chords.
- Any production credential or deployment requirement appears.

Handoff instructions:
- Hand off local API proof and changed files to `QA-05`.

Exact initialization prompt:

```text
You are WEB-03-BACKEND-MUSICXML-MAPPING. Work in `/Users/caleb/Documents/GitHub/akkordio-main`. Read `governance/source_truth.md`, `governance/agent_handoff_notes.md`, `governance/risk_register.md`, the DATA-01 and SCHEMA-02 audit files, then read `backend/main.py`, `backend/models.py`, `backend/parser.py`, `backend/layout_generator.py`, `backend/treble_mapping.py`, and `backend/bass_mapping.py`. Implement only the backend MusicXML upload-to-results pipeline for Phase 1 using `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`, B-system treble, and 120-bass Stradella. Do not touch frontend, PDF/OCR, Audiveris, Cloud Run, Render, or gh-pages. Do not mock results. Prove with local API/TestClient commands that `/upload_musicxml`, `/musicxml/{job_id}`, and `/results/{job_id}` return real data. Write `governance/governor_audits/WEB-03__2026-06-14__audit.md` with files read/changed, commands, tests, outputs, blockers, and handoff.
```

---

### UI-04-FRONTEND-RESULTS-INTEGRATION

Recommended model:
- `gpt-5.3-codex`, reasoning `medium`

Role:
- Frontend builder.

Mission:
- Integrate frontend MusicXML upload with real `/results/{job_id}` and render score plus accordion mapping.

Must read:
- `governance/source_truth.md`
- `governance/agent_handoff_notes.md`
- `governance/governor_audits/WEB-03__2026-06-14__audit.md`
- Canonical frontend files assigned by Root Governor after source/deploy reconciliation.

Allowed scope:
- Frontend API/upload/render integration only after backend passes QA.

Forbidden scope:
- No backend edits.
- No deployment changes.
- No PDF/OCR UI unless explicitly assigned.
- No duplicate-folder deletion.

Files/directories may edit:
- To be assigned by Root Governor after frontend canonical source decision.
- Audit file: `governance/governor_audits/UI-04__2026-06-14__audit.md`

Files/directories must not edit:
- `backend/**`
- `audiveris-service/**`
- `tools/**`

Required implementation steps:
1. Use real `job_id` from upload.
2. Fetch normalized MusicXML for OSMD.
3. Fetch real `/results/{job_id}`.
4. Render B-system treble and Stradella bass keyboards from backend layout data.
5. Show validation/unmapped summary if present.

Required verification:
- Local browser smoke with Bella Ciao.
- Console health check.
- Screenshot proof of score and keyboards.

Required deliverables:
- Changed frontend files.
- Audit file: `governance/governor_audits/UI-04__2026-06-14__audit.md`
- Screenshots or Browser proof.

Stop conditions:
- Backend not accepted by `QA-05`.
- Canonical frontend path unresolved.
- Browser proof cannot distinguish mock from live data.

Handoff instructions:
- Hand off to `QA-05` for end-to-end local validation.

Exact initialization prompt:

```text
You are UI-04-FRONTEND-RESULTS-INTEGRATION. Do not start until Root Governor confirms WEB-03 passed QA and names the canonical frontend path. Read `governance/source_truth.md`, `governance/agent_handoff_notes.md`, and `governance/governor_audits/WEB-03__2026-06-14__audit.md`. Your task is to wire MusicXML upload to real backend results: upload Bella Ciao, render MusicXML with OSMD, fetch `/results/{job_id}`, and render backend-provided B-system and Stradella layouts. Do not edit backend, deployment, PDF/OCR, or duplicate folders outside assigned scope. Prove with browser console logs, DOM/screenshot evidence, and exact commands. Write audit to `governance/governor_audits/UI-04__2026-06-14__audit.md`.
```

---

### QA-05-END-TO-END-AUDITOR

Recommended model:
- `gpt-5.3-codex`, reasoning `high`

Role:
- Auditor agent.

Mission:
- Independently verify DATA, SCHEMA, WEB, UI, and end-to-end Bella Ciao behavior.

Must read:
- `governance/source_truth.md`
- `governance/agent_handoff_notes.md`
- Relevant agent audit files.
- Git diff/status.
- Changed source files.

Allowed scope:
- Read files, run tests/commands, write audit.

Forbidden scope:
- No implementation edits unless explicitly re-scoped.
- No deployment changes.

Files/directories may edit:
- `governance/governor_audits/QA-05__2026-06-14__audit.md`

Files/directories must not edit:
- `backend/**`
- `frontend/**`
- `audiveris-service/**`

Required implementation steps:
1. Locate work orders and agent audit files.
2. Inspect actual diffs.
3. Run required verification commands.
4. Confirm scope compliance.
5. Confirm no secrets or mock data.
6. Write audit verdict recommendation for Root Governor.

Required verification:
- `git status --short --branch`
- `git diff --stat`
- Backend/API tests from WEB-03 audit.
- Browser tests from UI-04 audit if UI was changed.

Required deliverables:
- Audit file: `governance/governor_audits/QA-05__2026-06-14__audit.md`
- Verdict recommendation: PASS, PASS WITH CAVEATS, REPAIR REQUIRED, FAIL, or BLOCKED.

Stop conditions:
- Missing audit files.
- Required commands cannot be run.
- Claims lack objective evidence.

Handoff instructions:
- Hand off to `GOV-00` for final acceptance.

Exact initialization prompt:

```text
You are QA-05-END-TO-END-AUDITOR. Work in `/Users/caleb/Documents/GitHub/akkordio-main`. Read `governance/source_truth.md`, `governance/agent_handoff_notes.md`, `governance/agent_work_orders.md`, and all relevant agent audit files. You are inspection-only. Do not edit production code. Verify git status, diffs, commands, tests, API behavior, browser proof if applicable, scope compliance, secrets, and whether any mock data was used. Write `governance/governor_audits/QA-05__2026-06-14__audit.md` with objective evidence and a verdict recommendation for Root Governor.
```

---

### DEPLOY-06-DEPLOYMENT-HOSTING

Recommended model:
- `gpt-5.3-codex`, reasoning `high`

Role:
- Deployment agent.

Mission:
- Reconcile source/deploy flow and deploy only accepted work with local and hosted proof.

Must read:
- `governance/source_truth.md`
- `governance/risk_register.md`
- `governance/governor_audits/QA-05__2026-06-14__audit.md`
- `render.yaml`
- `cloudbuild.yaml` only if PDF/OCR phase is assigned
- GitHub Pages branch state

Allowed scope:
- Inspect deployment config.
- Propose or execute deployment steps only after Root Governor approval.

Forbidden scope:
- No secret printing.
- No production env var changes without explicit approval.
- No deploy before local proof and governor acceptance.

Files/directories may edit:
- Deployment docs under `governance/**`
- Deployment config only if explicitly assigned.

Files/directories must not edit:
- Backend/frontend implementation unless separately assigned.

Required implementation steps:
1. Reconcile `main` and `gh-pages` ownership.
2. Confirm build/test commands.
3. Confirm commit/push state.
4. Deploy only approved branch/artifact.
5. Smoke test hosted frontend and backend.

Required verification:
- Git commit hash.
- Build logs.
- Deployment logs or platform status.
- Hosted route smoke checks.

Required deliverables:
- Audit file: `governance/governor_audits/DEPLOY-06__2026-06-14__audit.md`

Stop conditions:
- Missing credentials.
- Local tests fail.
- Source/deploy flow unclear.
- Human approval required for env vars or production operations.

Handoff instructions:
- Hand off production proof to `GOV-00`.

Exact initialization prompt:

```text
You are DEPLOY-06-DEPLOYMENT-HOSTING. Do not deploy until Root Governor explicitly authorizes deployment. Work in `/Users/caleb/Documents/GitHub/akkordio-main` and read `governance/source_truth.md`, `governance/risk_register.md`, `governance/agent_handoff_notes.md`, and `governance/governor_audits/QA-05__2026-06-14__audit.md`. Your first task is to reconcile `main` vs `gh-pages` source/deploy flow and document required deployment proof. Never print secrets. Never change production environment variables without explicit approval. Write audit to `governance/governor_audits/DEPLOY-06__2026-06-14__audit.md`.
```
