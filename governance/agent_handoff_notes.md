# Agent Handoff Notes

Last updated: 2026-06-14  
Governor: `GOV-00`

## What Just Happened?

- Governance system was bootstrapped in `/Users/caleb/Documents/GitHub/akkordio-main/governance`.
- The project now has source truth, role identities, work orders, checklists, decision log, risk register, session log, prompt folder, archive folder, and governor audit folder.
- The prior implementation turn was interrupted after partial backend edits. Those edits are documented as unaccepted and must not be treated as complete.
- `DATA-01` verified the Bella Ciao fixture and produced an audit. `GOV-00` accepted it with caveats for Phase 1 planning input.
- `SCHEMA-02` defined the Phase 1 MusicXML upload/result contract and B-system/120-bass mapping policy. `GOV-00` accepted it with caveats as the contract source for backend implementation.
- Correction: DATA-01, SCHEMA-02, and WEB-03 were executed inline by the governor process before runtime sub-agent tooling was invoked. They are role/work-order artifacts, not independent runtime sub-agent sessions.
- Runtime sub-agents are now active for QA/governance inspection:
  - `QA-05`: multi-agent worker `019ec3a9-0f22-7922-99d8-f44a624fc098`
  - Governance integrity inspector: multi-agent explorer `019ec3a9-2880-71d2-a6a8-530fbe730510`
- Runtime `QA-05` independently verified the backend MusicXML path and wrote `governance/governor_audits/QA-05__2026-06-14__audit.md`.
- `GOV-00` accepted WEB-03 local backend behavior with caveats in `governance/governor_audits/GOVERNOR-WEB-03__2026-06-14__audit.md`.
- `DEPLOY-06` deployed commit `712b2a6` to Render service `accordi` and verified hosted backend behavior at `https://akkordio.onrender.com`.

## What Passed?

- The governor identified both worktrees:
  - `main`: `/Users/caleb/Documents/GitHub/akkordio-main`
  - `gh-pages`: `/Users/caleb/Documents/GitHub/akkordio`
- Governance folders were created.
- Governance docs were written.
- No duplicate folders were moved or deleted.
- Bella Ciao fixture exists, is a compressed `.mxl`, and parses with the backend parser.
- Parser output: 2 parts, 74 measures, 489 treble events, 514 bass events.
- Phase 1 contract exists at `governance/musicxml_mapping_contract.md`.
- `SCHEMA-02` is accepted as contract work, not implementation work.
- Local backend MusicXML upload-to-results now passes for Bella Ciao:
  - `/upload_musicxml` returns real `results_url`.
  - `/musicxml/{job_id}` returns normalized MusicXML.
  - `/results/{job_id}` returns 489 treble events and 514 bass events.
  - B-system treble and 120-bass Stradella validation both map 100% for this fixture.
- Hosted backend MusicXML upload-to-results also passes for Bella Ciao on Render:
  - Render deploy: `dep-d8n09ecm0tmc73djbb90`
  - hosted job: `e45b0383-b669-4c57-a4e8-f3fd575c7050`
  - `/upload_musicxml`, `/musicxml/{job_id}`, and `/results/{job_id}` all returned expected data.

## What Failed?

- PDF/OCR remains outside Phase 1 and is known unreliable.
- Frontend integration has not been accepted.
- Frontend canonical source/deploy flow is unresolved.

## What Is Blocked?

- Phase 1 backend MusicXML implementation is accepted locally with caveats.
- Runtime path hardening remains open because backend paths are relative to the process working directory.
- Backend deployment is complete for the MusicXML path.
- Frontend deployment/source ownership is still unresolved.

## What Should Happen Next?

1. User can test the hosted frontend against the deployed backend.
2. If frontend testing fails, inspect browser Network/Console and assign runtime `UI-04`.
3. Name the canonical frontend source path before any frontend code edits.

## Files/Artifacts That Matter

- Fixture: `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl`
- Canonical source: `/Users/caleb/Documents/GitHub/akkordio-main`
- Deployment worktree: `/Users/caleb/Documents/GitHub/akkordio`
- Governance root: `/Users/caleb/Documents/GitHub/akkordio-main/governance`
- DATA audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/DATA-01__2026-06-14__audit.md`
- Governor DATA audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/GOVERNOR-DATA-01__2026-06-14__audit.md`
- Phase 1 contract: `/Users/caleb/Documents/GitHub/akkordio-main/governance/musicxml_mapping_contract.md`
- SCHEMA audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`
- Governor SCHEMA audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/GOVERNOR-SCHEMA-02__2026-06-14__audit.md`
- WEB audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/WEB-03__2026-06-14__audit.md`
- QA audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/QA-05__2026-06-14__audit.md`
- Governor WEB audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/GOVERNOR-WEB-03__2026-06-14__audit.md`
- Deployment audit: `/Users/caleb/Documents/GitHub/akkordio-main/governance/governor_audits/DEPLOY-06__2026-06-14__audit.md`
- Accepted local backend modified files for WEB-03, pending commit/deployment:
  - `/Users/caleb/Documents/GitHub/akkordio-main/.gitignore`
  - `/Users/caleb/Documents/GitHub/akkordio-main/backend/bass_mapping.py`
  - `/Users/caleb/Documents/GitHub/akkordio-main/backend/main.py`
  - `/Users/caleb/Documents/GitHub/akkordio-main/backend/layout_generator.py`
  - `/Users/caleb/Documents/GitHub/akkordio-main/backend/models.py`
  - `/Users/caleb/Documents/GitHub/akkordio-main/backend/treble_mapping.py`

## What The Next Agent Must Not Misunderstand

- Do not assume PDF upload is in scope for Phase 1.
- Do not assume frontend upload/rendering is wired to the accepted backend output yet.
- Do not treat local backend acceptance as deployed production acceptance.
- Do not edit `gh-pages` unless assigned.
- Do not delete duplicate folders.
- Do not expose credentials or local token files.
- Do not present mock/fallback data as live proof.
- Do not assume the bass part is accordion-native; it is a piano-style bass clef part requiring explicit Stradella conversion rules.
- Do not treat `SCHEMA-02` acceptance as proof that backend endpoints work.
- Do not describe inline role execution as independent runtime sub-agent work. Actual runtime sub-agent IDs must be recorded when used.
- Do not treat local backend acceptance as frontend, hosted, or deployment acceptance.
- Hosted backend is now accepted for the MusicXML path, but frontend UI behavior is still unaccepted.
