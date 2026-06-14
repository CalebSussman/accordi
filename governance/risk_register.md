# Risk Register

| ID | Risk | Severity | Evidence | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Render memory exceeded by OEMER/PDF path | High | Prior triage reproduced job loss and Render 503 after OEMER processing. Human also reported Render memory exceeded. | Disable/gate OEMER; Phase 1 uses MusicXML only. | `WEB-03`, `DEPLOY-06` | Open |
| RISK-002 | Audiveris/Google Cloud PDF conversion is not end-to-end reliable | High | Audiveris processing failed parsing with `syntax error: line 1, column 0`. | Defer PDF/OCR to later phase; normalize `.mxl` before parser when revisited. | `DEPLOY-06` | Open |
| RISK-003 | Duplicate frontend trees cause drift | High | `main/frontend`, `gh-pages` root frontend, and `gh-pages/frontend` all exist. | Document canonical state; no UI work until source/deploy ownership is assigned. | `GOV-00`, `UI-04` | Open |
| RISK-004 | Partial unaccepted backend edits exist | Medium | Git status in `akkordio-main` shows modified backend files from interrupted turn. | Assign audit/repair work order before accepting or building on them. | `GOV-00`, `QA-05` | Open |
| RISK-005 | Mapping validation can be misleading | Medium | Previous baseline showed treble mapper dropped unmapped events, making validation appear better than source event count. | Require validation counts against original events and include unmapped reasons. | `SCHEMA-02`, `WEB-03` | Open |
| RISK-006 | Stradella bass conversion may misread piano-style left hand as accordion buttons | Medium | Bella Ciao left hand contains octave-specific notes/chords; Stradella buttons operate by bass/chord function. | Define deterministic bass conversion policy and report unsupported ambiguity. | `SCHEMA-02`, `WEB-03` | Open |
| RISK-007 | Local credentials could be exposed | High | `.codex/config.toml` in `gh-pages` worktree previously contained Render token. | Never print secrets; ensure local config dirs are ignored; audit diffs before commit. | `GOV-00`, `DEPLOY-06` | Open |
| RISK-008 | Production proof may be confused with local proof | Medium | Project has local, pushed, Pages, and Render states. | All audits must distinguish local, pushed, deployed, and production-live states. | All agents | Open |
