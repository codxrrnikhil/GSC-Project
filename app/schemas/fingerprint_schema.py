from datetime import datetime
from typing import List

from pydantic import BaseModel


class FingerprintSchema(BaseModel):
    id: str
    asset_id: str
    hash: str
    embedding: List[float]
    created_at: datetime
