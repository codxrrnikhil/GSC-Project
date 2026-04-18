import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.fingerprinting.image_fingerprint import generate_image_fingerprint
from app.services.fingerprinting.video_fingerprint import generate_video_fingerprint


router = APIRouter()


@router.post("/fingerprint")
def fingerprint_media(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1]
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file.file.read())
            temp_path = tmp_file.name

        content_type = file.content_type or ""
        if content_type.startswith("image/"):
            return generate_image_fingerprint(temp_path)
        if content_type.startswith("video/"):
            return generate_video_fingerprint(temp_path)

        raise HTTPException(status_code=400, detail="Only image or video uploads are supported.")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
