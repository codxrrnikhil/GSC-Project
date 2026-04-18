# GSC Project

## Overview

This project is a media protection pipeline with:
- FastAPI backend for fingerprinting, crawling, similarity detection, and logging
- Frontend UI for uploading media and viewing similarity results
- MongoDB persistence for assets, fingerprints, detections, feedback, and actions

## Tech Stack

- Python, FastAPI, Uvicorn
- MongoDB (PyMongo)
- CLIP (HuggingFace Transformers + Torch) for embeddings
- pHash (ImageHash) for image hashing
- OpenCV for video frame sampling
- Playwright and Scrapy for crawling
- Vite frontend (vanilla JS)

## Project Structure

- `app/` backend application
- `app/api/` API route handlers
- `app/services/` fingerprinting, crawling, similarity, and DB logic
- `app/models/` schema definitions for Mongo collections
- `app/db/migrations.py` collection/index bootstrap
- `frontend/` frontend UI

## Setup

### 1) Install backend dependencies

```bash
pip install -r requirements.txt
```

### 2) Run backend

```bash
python app/main.py
```

Backend runs on `http://localhost:8001` by default.

Optional custom port:

```bash
BACKEND_PORT=9000 python app/main.py
```

### 3) Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:8000` and points to backend `http://localhost:8001`.

## Pipeline Flow

1. Upload an image/video from frontend
2. Backend generates fingerprint:
   - image: pHash + CLIP embedding
   - video: 1 frame/sec sampling + averaged CLIP embedding
3. Similarity engine compares with stored fingerprints:
   - cosine similarity (embeddings)
   - hash similarity
4. Detection result is stored and shown in frontend with article URL
5. Feedback and action logs can be recorded

## Key API Routes

- `GET /` basic service info
- `GET /api/v1/health` health check
- `POST /api/v1/pipeline/assets` create asset + fingerprint from upload
- `GET /api/v1/pipeline/assets` list assets
- `POST /api/v1/pipeline/similarity` upload media + URL, run detection
- `GET /api/v1/pipeline/detections` list detections
- `POST /api/v1/pipeline/detections/{detection_id}/feedback` add feedback
- `POST /api/v1/pipeline/detections/{detection_id}/actions` log action
- `POST /crawl` and `POST /crawl-static` crawl URLs
- `POST /search-crawl` search then crawl top results

## Notes

- Keep backend and frontend on different ports (`8001` and `8000`).
- If CLIP downloads are slow, set `HF_TOKEN` for better HuggingFace limits.
- Restart backend after code changes when running without auto-reload.
