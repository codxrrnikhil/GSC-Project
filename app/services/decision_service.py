from datetime import datetime

from app.agents.content_agent import ContentAgent
from app.core.database import get_database


def process_content(data):
    agent = ContentAgent()
    decision = agent.decide(data)

    document = {
        "url": data.get("url", ""),
        "action": decision["action"],
        "confidence": decision["confidence"],
        "timestamp": datetime.utcnow(),
    }

    db = get_database()
    db.decisions.insert_one(document)

    return {
        "url": document["url"],
        "action": document["action"],
        "confidence": document["confidence"],
        "timestamp": document["timestamp"].isoformat(),
    }
