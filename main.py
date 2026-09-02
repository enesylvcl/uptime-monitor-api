# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
import contextlib

import models
import schemas
from database import engine, get_db
from checker import run_all_checks

models.Base.metadata.create_all(bind=engine)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_checks, "interval", seconds=30)
    scheduler.start()
    print("[Lifespan] APScheduler baslatildi.")
    run_all_checks()
    yield
    scheduler.shutdown()
    print("[Lifespan] APScheduler durduruldu.")

app = FastAPI(title="Uptime Monitor API", lifespan=lifespan)

@app.get("/dashboard")
def get_dashboard():
    return FileResponse("index.html")

@app.post("/targets", response_model=schemas.TargetResponse)
def create_target(target: schemas.TargetCreate, db: Session = Depends(get_db)):
    db_target = db.query(models.Target).filter(models.Target.url == target.url).first()
    if db_target:
        raise HTTPException(status_code=400, detail="Bu URL zaten ekli!")
    new_target = models.Target(name=target.name, url=target.url)
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    return new_target

@app.get("/targets", response_model=List[schemas.TargetResponse])
def get_targets(db: Session = Depends(get_db)):
    return db.query(models.Target).all()

@app.get("/targets/{target_id}", response_model=schemas.TargetResponse)
def get_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(models.Target).filter(models.Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Hedef bulunamadi!")
    return target

@app.get("/")
def read_root():
    return {"message": "Uptime Monitor API Aktif."}

@app.get("/checks", response_model=List[schemas.CheckResultResponse])
def get_latest_checks(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.CheckResult).order_by(models.CheckResult.timestamp.desc()).limit(limit).all()

@app.delete("/targets/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    target = db.query(models.Target).filter(models.Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Hedef bulunamadi")
    db.query(models.CheckResult).filter(models.CheckResult.target_id == target_id).delete()
    db.delete(target)
    db.commit()
    return {"message": "Silindi"}
