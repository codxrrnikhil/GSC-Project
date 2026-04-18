from fastapi import APIRouter
from app.core.database import get_database
from app.services.decision_service import process_content

router = APIRouter()

@router.post("/content")
def create_content(data: dict):
    db = get_database()
    result = db.contents.insert_one(data)
    return {"id": str(result.inserted_id), **data}

@router.get("/content")
def get_content():
    db = get_database()
    contents = list(db.contents.find({}, {"_id": 0}))
    return contents


@router.post("/analyze")
def analyze_content(data: dict):
    return process_content(data)