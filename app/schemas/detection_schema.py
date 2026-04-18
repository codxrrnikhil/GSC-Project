from datetime import datetime

from pydantic import BaseModel


class DetectionSchema(BaseModel):
    id: str
    url: str
    platform: str
    similarity_score: float
    matched_asset_id: str
    created_at: datetime
