# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# 1. Takip Edilen Siteler Tablosu (targets)
class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)                          # Orn: "Google"
    url = Column(String, unique=True, index=True)             # Orn: "https://www.google.com"

    # Bir sitenin birden cok kontrol sonucu olabilir
    checks = relationship("CheckResult", back_populates="target")


# 2. Kontrol Sonuclari Tablosu (check_results)
class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status_code = Column(Integer, nullable=True)               # Orn: 200, 404, 500
    response_time_ms = Column(Float, nullable=True)            # Orn: 204.79
    is_up = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)

    # Sonucun hangi siteye ait oldugunu baglar
    target = relationship("Target", back_populates="checks")