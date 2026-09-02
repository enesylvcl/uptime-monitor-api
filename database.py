# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL baglanti adresi (kullanici:sifre@sunucu:port/veritabani_adi)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/uptimedb"

# Veritabani ile konusacak motor (Engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Veritabani islemlerini yurutecek oturum yoneticisi (Session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo modellerimizin temel alacagi Base sinifi
Base = declarative_base()
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Yerel SQLite veritabani dosyasi (Sifir kurulum gerektirir)
SQLALCHEMY_DATABASE_URL = "sqlite:///./uptime.db"

# SQLite coklu is parcacigi ayari
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Veritabani islemlerini yurutecek oturum yoneticisi (Session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo modellerimizin temel alacagi Base sinifi
Base = declarative_base()

# Veritabani oturumu acip isi bitince kapatan yardimci fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Veritabani oturumu acip isi bitince kapatan yardimci fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
