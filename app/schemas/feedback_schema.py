from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FeedbackSchema(BaseModel):
    id: str
    detection_id: str
    user_decision: str
    correction: Optional[str] = None
    created_at: datetime
