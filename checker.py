# -*- coding: utf-8 -*-
# Ag istekleri atmak ve sureyi olcmek icin gerekli kutuphaneler
import time
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
import models


# Tek bir siteye HTTP GET istegi atar ve sonucu check_results tablosuna kaydeder
def check_target(target: models.Target, db: Session):
    # Bazi siteler bot gibi gorunen istekleri engelledigi icin normal bir tarayici kimligi gonderiyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    start_time = time.time()  # Istek gitmeden hemen onceki zaman
    try:
        # Siteye GET istegi gonderiyoruz; 10 saniyede cevap gelmezse hata firlatir
        response = requests.get(target.url, timeout=10, headers=headers)
        # Gecen sureyi milisaniyeye cevirip virgulden sonra 2 basamaga yuvarliyoruz
        duration = round((time.time() - start_time) * 1000, 2)
        # HTTP kodu 400'un altindaysa (200-399) site ayakta, 400 ve 500'ler erisilemiyor sayilir
        is_up = response.status_code < 400

        # Cevap geldiyse olcum sonucunu veritabani nesnesi olarak olusturuyoruz
        check_record = models.CheckResult(
            target_id=target.id,
            status_code=response.status_code,
            response_time_ms=duration,
            is_up=is_up,
            error_message=None if is_up else f"HTTP {response.status_code}"
        )
        status_text = "UP" if is_up else "DOWN"
        print(f"[Check] -> {target.name} ({target.url}): {status_text} | KOD: {response.status_code} | {duration}ms")

    except requests.RequestException as e:
        # Timeout, DNS bulunamadi, baglanti reddedildi gibi ag hatalarinda buraya duser
        duration = round((time.time() - start_time) * 1000, 2)
        check_record = models.CheckResult(
            target_id=target.id,
            status_code=None,             # Cevap gelmedigi icin HTTP kodu yok
            response_time_ms=duration,
            is_up=False,
            error_message=str(e)[:250]    # Hata metninin ilk 250 karakterini sakliyoruz
        )
        print(f"[Check] -> {target.name} HATA: {str(e)[:100]}")

    # Olcum sonucunu veritabanina kalici olarak kaydediyoruz
    db.add(check_record)
    db.commit()


# Veritabanindaki tum siteleri sirayla kontrol eder (zamanlayici bu fonksiyonu cagirir)
def run_all_checks():
    # Zamanlayici ayri bir thread'de calistigi icin kendi veritabani oturumunu acar
    db = SessionLocal()
    try:
        targets = db.query(models.Target).all()  # Kayitli tum siteleri al
        print(f"\n[Scheduler] Toplam {len(targets)} hedef kontrol ediliyor...")
        for target in targets:
            check_target(target, db)
        print("[Scheduler] Kontroller tamamlandi.\n")
    finally:
        db.close()  # Oturumu kapatiyoruz ki baglanti acik kalmasin
