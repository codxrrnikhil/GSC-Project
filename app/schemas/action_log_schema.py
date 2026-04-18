from datetime import datetime

from pydantic import BaseModel


class ActionLogSchema(BaseModel):
    id: str
    detection_id: str
    action_taken: str
    created_at: datetime
