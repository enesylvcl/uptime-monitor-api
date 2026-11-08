# -*- coding: utf-8 -*-
# Veritabani motorunu, temel model sinifini ve oturum olusturucuyu iceri aktariyoruz
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite veritabani dosyamizin konumu (ayni klasorde uptime.db adinda bir dosya olusturur, kurulum gerektirmez)
SQLALCHEMY_DATABASE_URL = "sqlite:///./uptime.db"

# Veritabani motorunu (engine) kuruyoruz:
# check_same_thread: False -> SQLite varsayilan olarak tek is parcacigiyla (thread) calisir.
# FastAPI istekleri ile arka plandaki zamanlayici ayri thread'lerde erissin diye bu kisitlamayi kaldiriyoruz.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Her islem icin bir oturum acacak fabrika nesnesi:
# autocommit=False -> Biz "db.commit()" demeden degisiklikleri kalici olarak kaydetmez.
# autoflush=False -> Sorgu yaparken hafizadaki nesneleri kendiliginden veritabanina gondermez.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo modellerimizin miras alacagi temel (Base) sinif
Base = declarative_base()


# FastAPI endpoint'lerinde Dependency Injection (bagimlilik enjeksiyonu) olarak kullandigimiz fonksiyon.
# Her gelen istekte yeni bir veritabani oturumu acar ve istek bitince kapatir.
def get_db():
    db = SessionLocal()
    try:
        yield db  # Oturumu istegi isleyen endpoint fonksiyonuna teslim eder
    finally:
        db.close()  # Istek basarili da olsa hata da olsa baglantiyi kapatir
