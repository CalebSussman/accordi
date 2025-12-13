# Audiveris Cloud Run Service

FastAPI wrapper around the Audiveris CLI for PDF → MusicXML conversion, intended for deployment to Google Cloud Run.

## Endpoints
- `GET /health` – readiness/liveness
- `POST /process` – accepts `file` (PDF), returns MusicXML (`.mxl` or `.musicxml`)

## Build & Deploy (Cloud Run)
```bash
gcloud run deploy audiveris-omr \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --allow-unauthenticated
```

If you require authentication:
```bash
gcloud run deploy audiveris-omr \
  --source . \
  --region us-central1 \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --no-allow-unauthenticated \
  --service-account <SERVICE_ACCOUNT_EMAIL> \
  --set-env-vars AUDIVERIS_TIMEOUT=600
```
- Grant your backend caller `roles/run.invoker` on the service:
  ```bash
  gcloud run services add-iam-policy-binding audiveris-omr \
    --region us-central1 \
    --member=serviceAccount:<BACKEND_SA_EMAIL> \
    --role=roles/run.invoker
  ```

## Runtime Configuration
- `AUDIVERIS_PATH` (optional): override path to Audiveris binary (default `/opt/Audiveris/bin/Audiveris`).
- `AUDIVERIS_TIMEOUT` (optional): processing timeout in seconds (default 300).
- `PORT` is set to `8080` for Cloud Run.

## Notes
- Container entrypoint is explicitly set to `uvicorn main:app --host 0.0.0.0 --port 8080` to satisfy Cloud Run health checks.
- Temporary files are stored under `/tmp/uploads` and `/tmp/output`. The input PDF is deleted after processing; outputs persist for the response.
- Ensure the Audiveris base image remains reachable; the Dockerfile pins to `jbarthelemy/audiveris:latest` as referenced in project plans.
