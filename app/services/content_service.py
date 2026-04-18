from datetime import datetime


def create_content(db, data):
    document = {
        "url": data.get("url", ""),
        "status": data.get("status", ""),
        "created_at": datetime.utcnow(),
    }
    result = db.contents.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return document


def get_all_contents(db):
    documents = list(db.contents.find())
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents
