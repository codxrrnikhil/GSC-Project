import json
import os
import re
import tempfile
from datetime import datetime
from io import BytesIO
from urllib.parse import urljoin
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image
import requests

from app.core.database import get_database
from app.schemas.pipeline import (
    ActionLogCreateRequest,
    AssetCreateRequest,
    DetectionCreateRequest,
    FeedbackCreateRequest,
)
from app.services.fingerprinting.image_fingerprint import generate_image_fingerprint
from app.services.fingerprinting.video_fingerprint import generate_video_fingerprint
from app.services.similarity_service import detect_similarity

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


def _stringify_id(value: Any) -> Any:
    return str(value) if value is not None else None


def _json_safe(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    doc = _json_safe(doc)
    doc["id"] = str(doc.pop("_id"))
    if "matched_asset_id" in doc:
        doc["matched_asset_id"] = _stringify_id(doc["matched_asset_id"])
    return doc


def _build_fingerprint(file: UploadFile, temp_path: str) -> dict[str, Any]:
    content_type = file.content_type or ""
    if content_type.startswith("image/"):
        return generate_image_fingerprint(temp_path)
    if content_type.startswith("video/"):
        return generate_video_fingerprint(temp_path)
    raise HTTPException(status_code=400, detail="Only image or video uploads are supported.")


def _extract_candidate_image_urls(article_url: str) -> list[str]:
    try:
        response = requests.get(article_url, timeout=15)
        response.raise_for_status()
        html = response.text
    except Exception:
        return []

    candidates: list[str] = []

    og_match = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        html,
        flags=re.IGNORECASE,
    )
    if og_match:
        candidates.append(urljoin(article_url, og_match.group(1)))

    for src in re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        candidates.append(urljoin(article_url, src))
        if len(candidates) >= 5:
            break

    seen = set()
    unique: list[str] = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _fingerprint_remote_image(image_url: str) -> dict[str, Any] | None:
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            image.save(tmp_file.name, format="JPEG")
            temp_path = tmp_file.name
        try:
            return generate_image_fingerprint(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception:
        return None


@router.post("/assets")
def create_asset_with_fingerprint(
    owner: str = Form(...),
    metadata_json: str = Form("{}"),
    file: UploadFile = File(...),
):
    db = get_database()
    temp_path = None

    try:
        payload = AssetCreateRequest(owner=owner, metadata=json.loads(metadata_json))

        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file.file.read())
            temp_path = tmp_file.name

        fingerprint = _build_fingerprint(file, temp_path)
        asset_doc = {
            "owner": payload.owner,
            "metadata": payload.metadata,
            "created_at": datetime.utcnow(),
        }
        asset_result = db.assets.insert_one(asset_doc)
        asset_id = str(asset_result.inserted_id)

        fp_doc = {
            "asset_id": asset_id,
            "hash": fingerprint.get("hash"),
            "embedding": fingerprint.get("embedding", []),
            "created_at": datetime.utcnow(),
        }
        fp_result = db.fingerprints.insert_one(fp_doc)

        return {
            "asset_id": asset_id,
            "fingerprint_id": str(fp_result.inserted_id),
            "hash": fp_doc["hash"],
            "embedding_size": len(fp_doc["embedding"]),
        }
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="metadata_json must be valid JSON.") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/assets")
def list_assets():
    db = get_database()
    docs = list(db.assets.find().sort("created_at", -1))
    return [_serialize(doc) for doc in docs]


@router.post("/similarity")
def detect_similarity_for_upload(
    url: str = Form(...),
    platform: str = Form(...),
    file: UploadFile = File(...),
):
    db = get_database()
    temp_path = None

    try:
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file.file.read())
            temp_path = tmp_file.name

        fingerprint = _build_fingerprint(file, temp_path)
        all_fingerprints = list(db.fingerprints.find({}, {"asset_id": 1, "hash": 1, "embedding": 1}))
        match = detect_similarity(
            fingerprint.get("embedding", []),
            all_fingerprints,
            content_hash=fingerprint.get("hash"),
        )
        url_best_score = 0.0
        matched_image_url = None
        for candidate_url in _extract_candidate_image_urls(url):
            remote_fp = _fingerprint_remote_image(candidate_url)
            if not remote_fp:
                continue
            score_result = detect_similarity(
                fingerprint.get("embedding", []),
                [
                    {
                        "asset_id": candidate_url,
                        "hash": remote_fp.get("hash"),
                        "embedding": remote_fp.get("embedding", []),
                    }
                ],
                content_hash=fingerprint.get("hash"),
            )
            if score_result["similarity_score"] > url_best_score:
                url_best_score = float(score_result["similarity_score"])
                matched_image_url = candidate_url

        final_score = max(float(match["similarity_score"]), url_best_score)
        matched_asset_id = _stringify_id(match["matched_asset_id"])
        detection = DetectionCreateRequest(
            url=url,
            platform=platform,
            similarity_score=final_score,
            matched_asset_id=matched_asset_id,
        )
        doc = {
            "url": detection.url,
            "platform": detection.platform,
            "similarity_score": detection.similarity_score,
            "matched_asset_id": detection.matched_asset_id,
            "matched_image_url": matched_image_url,
            "url_similarity_score": url_best_score,
            "timestamp": datetime.utcnow(),
        }
        inserted = db.detections.insert_one(doc)
        return _json_safe({"detection_id": str(inserted.inserted_id), **doc})
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/detections/{detection_id}/feedback")
def add_feedback(detection_id: str, body: FeedbackCreateRequest):
    db = get_database()
    doc = {
        "detection_id": detection_id,
        "user_decision": body.user_decision,
        "correction": body.correction,
        "created_at": datetime.utcnow(),
    }
    result = db.user_feedback.insert_one(doc)
    return _json_safe({"feedback_id": str(result.inserted_id), **doc})


@router.post("/detections/{detection_id}/actions")
def log_action(detection_id: str, body: ActionLogCreateRequest):
    db = get_database()
    doc = {
        "detection_id": detection_id,
        "action_taken": body.action_taken,
        "created_at": datetime.utcnow(),
    }
    result = db.actions_taken.insert_one(doc)
    return _json_safe({"action_id": str(result.inserted_id), **doc})


@router.post("/detections")
def create_detection(body: DetectionCreateRequest):
    db = get_database()
    doc = {
        "url": body.url,
        "platform": body.platform,
        "similarity_score": body.similarity_score,
        "matched_asset_id": _stringify_id(body.matched_asset_id),
        "timestamp": datetime.utcnow(),
    }
    result = db.detections.insert_one(doc)
    return _json_safe({"detection_id": str(result.inserted_id), **doc})


@router.get("/detections")
def list_detections():
    db = get_database()
    docs = list(db.detections.find().sort("timestamp", -1))
    return [_serialize(doc) for doc in docs]
