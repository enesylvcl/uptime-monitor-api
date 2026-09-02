# -*- coding: utf-8 -*-
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Kontrol Sonuclari Semalari ---
class CheckResultBase(BaseModel):
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    is_up: bool
    error_message: Optional[str] = None

class CheckResultResponse(CheckResultBase):
    id: int
    target_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# --- Hedef Site Semalari ---
class TargetBase(BaseModel):
    name: str
    url: str

class TargetCreate(TargetBase):
    pass  # Yeni site eklerken sadece name ve url bekliyoruz

class TargetResponse(TargetBase):
    id: int
    checks: List[CheckResultResponse] = []

    class Config:
        from_attributes = True  # SQLAlchemy nesnelerini otomatik JSON formatina cevirir