# Agent Checklists

Checklist items are only completed after objective proof and governor acceptance.

## Governance Bootstrap

- [x] Create governance directory structure - Responsible: `GOV-00` - Completed: 2026-06-14 - Audit: `governance/governor_audits/GOVERNOR-GOV-00__2026-06-14__audit.md`
- [x] Record canonical source truth and duplicate folders - Responsible: `GOV-00` - Completed: 2026-06-14 - Audit: `governance/governor_audits/GOVERNOR-GOV-00__2026-06-14__audit.md`
- [x] Create master work-order roster - Responsible: `GOV-00` - Completed: 2026-06-14 - Audit: `governance/governor_audits/GOVERNOR-GOV-00__2026-06-14__audit.md`

## Phase 1: Bella Ciao MusicXML Baseline

- [x] Verify Bella Ciao fixture metadata and parse shape - Responsible: `DATA-01` - Execution: inline governor role work - Completed: 2026-06-14 - Audit: `governance/governor_audits/DATA-01__2026-06-14__audit.md`; Governor audit: `governance/governor_audits/GOVERNOR-DATA-01__2026-06-14__audit.md`
- [x] Define MusicXML upload/result API contract - Responsible: `SCHEMA-02` - Execution: inline governor role work - Completed: 2026-06-14 - Audit: `governance/governor_audits/SCHEMA-02__2026-06-14__audit.md`; Governor audit: `governance/governor_audits/GOVERNOR-SCHEMA-02__2026-06-14__audit.md`
- [x] Implement backend MusicXML mapping pipeline - Responsible: `WEB-03` - Execution: inline governor role work verified by runtime `QA-05` sub-agent `019ec3a9-0f22-7922-99d8-f44a624fc098` - Completed: 2026-06-14 - Audit: `governance/governor_audits/WEB-03__2026-06-14__audit.md`; QA audit: `governance/governor_audits/QA-05__2026-06-14__audit.md`; Governor audit: `governance/governor_audits/GOVERNOR-WEB-03__2026-06-14__audit.md`
- [x] Integrate frontend with real `/results/{job_id}` data - Responsible: `UI-04` - Runtime sub-agent: `019ec3d0-d8d0-7be0-9966-9e1c24475591` - Completed: 2026-06-14 - Audit: `governance/governor_audits/UI-04__2026-06-14__audit.md`; Governor audit: `governance/governor_audits/GOVERNOR-UI-04__2026-06-14__audit.md`
- [x] Run backend Bella Ciao QA for MusicXML path - Responsible: `QA-05` - Runtime sub-agent: `019ec3a9-0f22-7922-99d8-f44a624fc098` - Completed: 2026-06-14 - Audit: `governance/governor_audits/QA-05__2026-06-14__audit.md`; Governor audit: `governance/governor_audits/GOVERNOR-WEB-03__2026-06-14__audit.md`

## Deployment

- [x] Deploy accepted backend MusicXML pipeline to Render - Responsible: `DEPLOY-06` - Completed: 2026-06-14 - Audit: `governance/governor_audits/DEPLOY-06__2026-06-14__audit.md`
- [ ] Reconcile `main` vs `gh-pages` frontend source/deployment flow - Responsible: `DEPLOY-06` - Audit: TBD
- [ ] Deploy frontend only after frontend proof passes - Responsible: `DEPLOY-06` - Audit: TBD
