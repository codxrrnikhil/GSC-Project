from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AssetSchema(BaseModel):
    id: str
    owner: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
