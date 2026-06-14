# DEPLOY-06 Audit

Date: 2026-06-14  
Agent: `DEPLOY-06`  
Runtime inspector sub-agent: `019ec3b8-943e-71c2-aa38-c7db7343ff98`  
Verdict recommendation: PASS WITH CAVEATS

## Task Summary

Deployed the accepted Phase 1 backend MusicXML mapping pipeline to Render service `accordi` at `https://akkordio.onrender.com` and verified hosted behavior with the Bella Ciao `.mxl` fixture.

## Files Changed

Deployment commit included:

- `.gitignore`
- `Dockerfile`
- `backend/bass_mapping.py`
- `backend/layout_generator.py`
- `backend/main.py`
- `backend/models.py`
- `backend/treble_mapping.py`
- `governance/**`

No frontend files were changed.

## Commands Run

```sh
git status --short --branch
git remote -v
sed -n '1,220p' render.yaml
sed -n '1,240p' Dockerfile
git diff --check
.venv/bin/python -m py_compile backend/main.py backend/models.py backend/parser.py backend/layout_generator.py backend/treble_mapping.py backend/bass_mapping.py
git add .gitignore Dockerfile backend/bass_mapping.py backend/layout_generator.py backend/main.py backend/models.py backend/treble_mapping.py governance
git commit -m "Deploy MusicXML backend mapping pipeline"
git remote set-url origin git@github.com:CalebSussman/accordi.git
ssh -T git@github.com
git push origin main
```

Render API actions:

- Listed services using local Render API configuration without printing credentials.
- Found service:
  - service name: `accordi`
  - service ID: `srv-d4r3c42dbo4c73c56mgg`
  - URL: `https://akkordio.onrender.com`
  - autoDeploy: `no`
- Triggered manual deploy:
  - deploy ID: `dep-d8n09ecm0tmc73djbb90`
  - commit: `712b2a66a377480b9d46cd91fc583a21f004c5de`
  - trigger: `api`
- Polled deploy until status `live`.

Hosted smoke command:

```sh
.venv/bin/python -W ignore - <<'PY'
import json
from pathlib import Path
import requests
base = 'https://akkordio.onrender.com'
fixture = Path('/Users/caleb/Downloads/Bella_Ciao_-_La_Casa_de_Papel.mxl')
health = requests.get(f'{base}/health', timeout=60)
with fixture.open('rb') as fh:
    upload = requests.post(f'{base}/upload_musicxml', files={'file': (fixture.name, fh, 'application/vnd.recordare.musicxml')}, timeout=180)
body = upload.json()
job_id = body['job_id']
status = requests.get(f'{base}/status/{job_id}', timeout=60)
musicxml = requests.get(f'{base}/musicxml/{job_id}', timeout=60)
results = requests.get(f'{base}/results/{job_id}', timeout=60)
data = results.json()
assert len(data.get('treble_events', [])) == 489
assert len(data.get('bass_events', [])) == 514
assert data.get('treble_layout_id') == 'b_system_5row'
assert data.get('bass_layout_id') == 'stradella_120'
assert data['validation']['treble']['source_events'] == 489
assert data['validation']['treble']['mapped_events'] == 489
assert data['validation']['bass']['source_events'] == 514
assert data['validation']['bass']['mapped_events'] == 514
PY
```

## Build Results

Local Python compile passed.

Render deploy:

```text
dep-d8n09ecm0tmc73djbb90 live
commit 712b2a66a377480b9d46cd91fc583a21f004c5de
finishedAt 2026-06-14T01:37:07.45146Z
```

## Hosted Smoke Results

Health:

```text
GET https://akkordio.onrender.com/health
200 {"status":"healthy","service":"akkordio-backend"}
```

Upload:

```json
{
  "success": true,
  "job_id": "e45b0383-b669-4c57-a4e8-f3fd575c7050",
  "status": "completed",
  "musicxml_url": "/musicxml/e45b0383-b669-4c57-a4e8-f3fd575c7050",
  "results_url": "/results/e45b0383-b669-4c57-a4e8-f3fd575c7050",
  "message": "MusicXML mapped successfully"
}
```

Hosted results:

```json
{
  "treble_events": 489,
  "bass_events": 514,
  "treble_layout_id": "b_system_5row",
  "bass_layout_id": "stradella_120",
  "treble_mapped_events": 489,
  "bass_mapped_events": 514,
  "musicxml_bytes": 536714
}
```

Representative bass proof:

```json
{
  "first_bass": {"row": 1, "column": 4, "midi": 40, "note": "E", "label": "E", "type": "root"},
  "first_chord": {"row": 3, "column": 8, "midi": 44, "note": "G#", "label": "G#m", "type": "minor"}
}
```

## Data/Database Changes

No database exists or was changed. Hosted test created a Render-local in-memory/disk job:

- `e45b0383-b669-4c57-a4e8-f3fd575c7050`

This is normal runtime output and may disappear on service restart because job status is in memory and files are container-local.

## Deployment Changes

- Commit created locally: `712b2a6 Deploy MusicXML backend mapping pipeline`
- Commit pushed to `origin/main`.
- Render service `accordi` manually deployed commit `712b2a66a377480b9d46cd91fc583a21f004c5de`.
- `origin` remote was changed from HTTPS to SSH to allow authenticated push.

## Known Caveats

- Render auto-deploy is `no`; future deploys require manual trigger or enabling auto-deploy.
- Frontend hosted UI was not browser-tested by this deploy audit. Backend cloud API is verified.
- Backend jobs/results are not durable across Render restarts.
- PDF/OCR/Audiveris remains out of scope and should not be used as proof.
- Render MCP workspace selection remained unavailable; Render REST API was used with local config without printing credentials.

## Handoff Recommendation

Frontend cloud testing can proceed against `https://akkordio.onrender.com`. If the frontend still fails, treat it as a frontend integration/UI issue unless Network tab shows a backend non-200 response.
