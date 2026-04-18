from fastapi import APIRouter

from app.services.mongodb import db


router = APIRouter()


@router.get("/test-db")
async def test_db_connection():
    document = {"status": "ok", "source": "connection_test"}
    result = await db.test_collection.insert_one(document)
    return {"inserted_id": str(result.inserted_id)}
