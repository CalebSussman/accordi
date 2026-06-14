# Governor Audit: SCHEMA-02

Date: 2026-06-14  
Governor: `GOV-00`  
Audited role/work-order artifact: `SCHEMA-02`  
Work order: `SCHEMA-02-MUSICXML-MAPPING-CONTRACT`  
Verdict: PASS WITH CAVEATS

Execution provenance: this audit reviewed inline governor-executed role work, not an independent runtime sub-agent session.

## Scope Audited

The inline `SCHEMA-02` role work was assigned to define the Phase 1 MusicXML upload/result contract and B-system/120-bass mapping policy. It was not assigned to implement endpoints, edit frontend code, change deployment, or repair the interrupted backend changes.

## Evidence Inspected

Files inspected:

- `governance/agent_work_orders.md`
- `governance/agent_checklists.md`
- `governance/agent_handoff_notes.md`
- `governance/agent_session_log.md`
- `governance/musicxml_mapping_contract.md`
- `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`

Commands run:

```sh
pwd && git status --short --branch
sed -n '1,260p' governance/musicxml_mapping_contract.md
sed -n '261,520p' governance/musicxml_mapping_contract.md
sed -n '1,220p' governance/governor_audits/SCHEMA-02__2026-06-14__audit.md
sed -n '1,260p' governance/agent_checklists.md
sed -n '1,260p' governance/agent_handoff_notes.md
sed -n '1,320p' governance/agent_session_log.md
sed -n '1,220p' governance/agent_work_orders.md
sed -n '220,520p' governance/agent_work_orders.md
rg -n "upload_musicxml|stradella_120|source_events|button_position|selected_position|unmapped|Bella Ciao" governance/musicxml_mapping_contract.md governance/governor_audits/SCHEMA-02__2026-06-14__audit.md
```

Git status at audit time:

```text
## main...origin/main
 M .gitignore
 M backend/bass_mapping.py
 M backend/layout_generator.py
 M backend/models.py
 M backend/treble_mapping.py
?? governance/
```

The modified backend files predate this schema audit and remain unaccepted.

## Findings

- `governance/musicxml_mapping_contract.md` exists and defines Phase 1 scope for `.mxl`, `.musicxml`, and `.xml` upload-to-results.
- The contract explicitly excludes PDF/OCR, OEMER, Audiveris, Cloud Run, deployment, and frontend source/deploy reconciliation.
- The contract defines `POST /upload_musicxml`, `GET /musicxml/{job_id}`, and `GET /results/{job_id}` behavior.
- The contract requires `.mxl` normalization to `processed/{job_id}/{job_id}.musicxml`.
- The contract requires real `processed/{job_id}/result.json` output and forbids mock `results_url`.
- The contract defines treble event preservation, explicit unmapped event behavior, and deterministic `selected_position`.
- The contract defines bass single-note pitch-class mapping and supported Stradella chord rows for 120-bass layout.
- The contract defines validation fields and requires `mapped_events + unmapped_events == source_events`.
- Bella Ciao fixture counts from `DATA-01` are carried forward: 489 treble source events and 514 bass source events.
- The SCHEMA audit file exists and states that no backend, frontend, data, or deployment changes were made by this task.

## Scope Compliance

Inline SCHEMA-02 role work stayed within documentation/schema scope. No accepted evidence shows edits to production backend, frontend, deployment, fixture, or duplicate folders.

## Caveats

- This is a contract acceptance only. It does not prove that the backend implements the contract.
- The worktree still contains pre-existing unaccepted backend edits from an interrupted implementation turn.
- Frontend source/deploy ownership remains unresolved and must not be assumed by WEB-03.
- The contract relies on parser/music21 chord classification; WEB-03 must preserve transparent unmapped reasons where classification is unsupported or ambiguous.

## Governor Decision

PASS WITH CAVEATS. `SCHEMA-02` is accepted as the Phase 1 contract source for `WEB-03`. Implementation remains unaccepted until `WEB-03` produces code, objective local API proof, and an audit file.

## Handoff

Proceed to `WEB-03-BACKEND-MUSICXML-MAPPING` under the existing work order. WEB-03 must read `governance/musicxml_mapping_contract.md`, account for the dirty worktree, avoid PDF/OCR/frontend/deployment scope, and prove Bella Ciao through local API/TestClient verification.
