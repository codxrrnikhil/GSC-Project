from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AssetCreateRequest(BaseModel):
    owner: str = Field(..., min_length=1)
    metadata: Optional[dict[str, Any]] = None


class DetectionCreateRequest(BaseModel):
    url: str = Field(..., min_length=1)
    platform: str = Field(..., min_length=1)
    similarity_score: float
    matched_asset_id: Optional[str] = None


class FeedbackCreateRequest(BaseModel):
    user_decision: str = Field(..., min_length=1)
    correction: Optional[str] = None


class ActionLogCreateRequest(BaseModel):
    action_taken: str = Field(..., min_length=1)


class DetectionResponse(BaseModel):
    id: str
    url: str
    platform: str
    similarity_score: float
    matched_asset_id: Optional[str] = None
    timestamp: datetime
