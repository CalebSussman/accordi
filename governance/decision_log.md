# Decision Log

## 2026-06-14 - Establish Governance System

- Decision: Use `/Users/caleb/Documents/GitHub/akkordio-main` on branch `main` as the canonical governance/source worktree.
- Reason: `main` contains backend, refs, deployment config, and source documentation. `gh-pages` is deployment/frontend-only and contains duplicate frontend artifacts.
- Owner: `GOV-00`

## 2026-06-14 - Phase 1 Direction

- Decision: Phase 1 must start from MusicXML/MXL upload, not PDF/OCR.
- Reason: Render memory failures make OEMER unsuitable; Audiveris path is not yet end-to-end reliable. MusicXML upload is the only proven viable base path.
- Owner: `GOV-00`

## 2026-06-14 - Baseline Instrument

- Decision: Use B-system treble plus 120-bass Stradella as Phase 1 baseline.
- Reason: Human explicitly requested dynamic implementation initially based on a B-system 120-bass accordion.
- Owner: `GOV-00`

## 2026-06-14 - Primary Fixture

- Decision: Use `/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl` as the first Phase 1 fixture.
- Reason: Human explicitly provided this file to start validation.
- Owner: `GOV-00`

## 2026-06-14 - No Deletion Of Duplicates

- Decision: Duplicate frontend folders and worktrees are documented but not moved/deleted.
- Reason: Human instructed not to move or delete without authorization.
- Owner: `GOV-00`
