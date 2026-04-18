def create_asset(db, data):
    result = db.assets.insert_one(data)
    return str(result.inserted_id)


def store_fingerprint(db, data):
    result = db.fingerprints.insert_one(data)
    return str(result.inserted_id)


def create_detection(db, data):
    result = db.detections.insert_one(data)
    return str(result.inserted_id)


def add_feedback(db, data):
    result = db.user_feedback.insert_one(data)
    return str(result.inserted_id)


def log_action(db, data):
    result = db.actions_taken.insert_one(data)
    return str(result.inserted_id)
