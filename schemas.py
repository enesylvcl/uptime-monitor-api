# -*- coding: utf-8 -*-
# Gelen/giden verinin tiplerini dogrulamak ve API'nin JSON sablonlarini tanimlamak icin Pydantic kullaniyoruz
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# --- Kontrol Sonuclari Semalari ---

# Kontrol sonucunun ortak alanlari
class CheckResultBase(BaseModel):
    status_code: Optional[int] = None         # Sayi veya (baglanti kurulamadiysa) None
    response_time_ms: Optional[float] = None  # Milisaniye cinsinden sure veya None
    is_up: bool                               # True veya False olmak zorunda
    error_message: Optional[str] = None       # Varsa hata mesaji, yoksa None


# Kullaniciya kontrol sonucunu donerken kullanilan sema (ID, site ID'si ve zaman eklenir)
class CheckResultResponse(CheckResultBase):
    id: int
    target_id: int
    timestamp: datetime

    # SQLAlchemy nesnesinin alanlarini okuyup JSON'a cevirebilmesini saglar
    model_config = ConfigDict(from_attributes=True)


# --- Hedef Site Semalari ---

# Hedef sitenin temel alanlari (kullanicidan beklenen bilgiler)
class TargetBase(BaseModel):
    name: str  # Site adi (zorunlu)
    url: str   # Site adresi (zorunlu)


# POST /targets ile yeni site eklerken kullanilan sema: sadece name ve url bekler
class TargetCreate(TargetBase):
    pass


# Site bilgisini geri donerken kullanilan sema (ID ve gecmis kontrol sonuclari eklenir)
class TargetResponse(TargetBase):
    id: int                                 # Veritabaninin atadigi ID
    checks: List[CheckResultResponse] = []  # Bu siteye ait gecmis olcumlerin listesi

    # SQLAlchemy nesnesinin alanlarini okuyup JSON'a cevirebilmesini saglar
    model_config = ConfigDict(from_attributes=True)
