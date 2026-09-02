import time
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def check_target(target: models.Target, db: Session):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    start_time = time.time()
    try:
        response = requests.get(target.url, timeout=10, headers=headers)
        duration = round((time.time() - start_time) * 1000, 2)
        is_up = response.status_code < 400

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
        duration = round((time.time() - start_time) * 1000, 2)
        check_record = models.CheckResult(
            target_id=target.id,
            status_code=None,
            response_time_ms=duration,
            is_up=False,
            error_message=str(e)[:250]
        )
        print(f"[Check] -> {target.name} HATA: {str(e)[:100]}")

    db.add(check_record)
    db.commit()

def run_all_checks():
    db = SessionLocal()
    try:
        targets = db.query(models.Target).all()
        print(f"\n[Scheduler] Toplam {len(targets)} hedef kontrol ediliyor...")
        for target in targets:
            check_target(target, db)
        print("[Scheduler] Kontroller tamamlandi.\n")
    finally:
        db.close()
