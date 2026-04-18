from app.core.database import get_database


def run_migrations():
    db = get_database()

    # Collections used by the detection pipeline.
    collections = ["assets", "fingerprints", "detections", "user_feedback", "actions_taken"]
    existing = set(db.list_collection_names())
    for name in collections:
        if name not in existing:
            db.create_collection(name)

    db.assets.create_index("owner")
    db.fingerprints.create_index("asset_id")
    db.detections.create_index([("timestamp", -1)])
    db.user_feedback.create_index("detection_id")
    db.actions_taken.create_index("detection_id")
