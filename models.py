# -*- coding: utf-8 -*-
# Tablo sutun tiplerini, SQL fonksiyonlarini ve tablo iliskilerini iceri aktariyoruz
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


# 1. Takip Edilen Siteler Tablosu (targets)
class Target(Base):
    __tablename__ = "targets"  # Veritabanindaki tablonun adi

    id = Column(Integer, primary_key=True, index=True)  # Her sitenin benzersiz kimlik numarasi (1, 2, 3...)
    name = Column(String, index=True)                   # Sitenin takma adi (Orn: "Google")
    url = Column(String, unique=True, index=True)       # Sitenin adresi; unique=True sayesinde ayni URL 2 kez eklenemez

    # Bire-Cok (One-to-Many) iliski: 1 sitenin birden cok kontrol sonucu olabilir.
    # "target.checks" yazinca o sitenin tum gecmis olcumleri liste olarak gelir.
    # order_by: liste her zaman eskiden yeniye siralanir, boylece listenin son elemani en son kontroldur.
    # (CheckResult sinifi asagida tanimlandigi icin isim metin olarak yaziliyor.)
    checks = relationship("CheckResult", back_populates="target", order_by="CheckResult.timestamp")


# 2. Kontrol Sonuclari Tablosu (check_results)
class CheckResult(Base):
    __tablename__ = "check_results"  # Kontrol sonuclarinin tutuldugu tablonun adi

    id = Column(Integer, primary_key=True, index=True)  # Olcum kaydinin benzersiz ID'si

    # Yabanci Anahtar (Foreign Key): Bu olcumun hangi siteye ait oldugunu targets tablosundaki id ile eslestirir
    target_id = Column(Integer, ForeignKey("targets.id"), index=True)

    # Olcumun yapildigi tarih ve saat; kayit eklenirken veritabani tarafindan otomatik yazilir
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    status_code = Column(Integer, nullable=True)        # Siteden donen HTTP kodu (200, 404, 500...). Baglanti kurulamadiysa bos kalir
    response_time_ms = Column(Float, nullable=True)     # Sitenin yanit suresi (milisaniye), orn: 204.79
    is_up = Column(Boolean, default=False)              # Site erisilebilir mi? (True: ayakta, False: erisilemiyor)
    error_message = Column(String, nullable=True)       # Hata olduysa aciklamasi (orn: "HTTP 500", timeout, baglanti hatasi)

    # Ters iliski: "check_result.target" dendiginde bu sonucun ait oldugu Target nesnesini verir
    target = relationship("Target", back_populates="checks")
