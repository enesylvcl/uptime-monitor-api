# Uptime Monitor API

Kayıtlı web sitelerinin **erişilebilir olup olmadığını periyodik olarak kontrol eden** bir REST API. Arka planda çalışan bir zamanlayıcı her 30 saniyede bir tüm sitelere HTTP isteği atar; sonucu (durum kodu, yanıt süresi, ayakta mı / erişilemiyor mu) veritabanına kaydeder. Sonuçlar API üzerinden ve basit bir web dashboard'u üzerinden görüntülenebilir.

## Kullanılan Teknolojiler

- **FastAPI** – REST API ve endpoint'ler
- **SQLAlchemy** – ORM (Python sınıfları ↔ veritabanı tabloları)
- **SQLite** – Veritabanı (`uptime.db` dosyası, kurulum gerektirmez)
- **Pydantic** – İstek/yanıt verilerinin doğrulanması (şemalar)
- **APScheduler** – Arka planda periyodik kontrol (BackgroundScheduler)
- **requests** – Sitelere HTTP GET isteği atmak
- **Uvicorn** – Uygulamayı çalıştıran ASGI sunucusu

## Klasör Yapısı

```
uptime-monitor-api/
├── main.py                    # FastAPI uygulaması, endpoint'ler ve zamanlayıcının başlatılması
├── checker.py                 # Kontrol mantığı: sitelere istek atar, sonucu kaydeder
├── database.py                # SQLite bağlantısı, oturum (session) ve get_db fonksiyonu
├── models.py                  # Veritabanı tabloları (Target, CheckResult)
├── schemas.py                 # Pydantic şemaları (API giriş/çıkış formatları)
├── index.html                 # Dashboard arayüzü (GET /dashboard ile sunulur)
├── requirements.txt           # Python bağımlılıkları
├── uptime-monitor-api.sln     # Visual Studio çözüm dosyası
├── uptime-monitor-api.pyproj  # Visual Studio Python proje dosyası
├── .gitignore
└── .gitattributes
```

## Veritabanı Tabloları

**`targets`** – Takip edilen siteler

| Sütun | Tip | Açıklama |
|---|---|---|
| `id` | Integer (PK) | Sitenin kimlik numarası |
| `name` | String | Sitenin adı (örn. "Google") |
| `url` | String (unique) | Sitenin adresi; aynı URL iki kez eklenemez |

**`check_results`** – Her kontrolün sonucu

| Sütun | Tip | Açıklama |
|---|---|---|
| `id` | Integer (PK) | Kontrol kaydının kimlik numarası |
| `target_id` | Integer (FK → targets.id) | Kontrolün ait olduğu site |
| `timestamp` | DateTime | Kontrolün zamanı (veritabanı otomatik yazar) |
| `status_code` | Integer, boş olabilir | HTTP durum kodu; bağlantı kurulamadıysa boş |
| `response_time_ms` | Float, boş olabilir | Yanıt süresi (milisaniye) |
| `is_up` | Boolean | Site ayakta mı |
| `error_message` | String, boş olabilir | Hata açıklaması (örn. `HTTP 404` veya bağlantı hatası) |

İlişki: bir `Target`'ın birden çok `CheckResult`'ı vardır (one-to-many). `target.checks` listesi zamana göre eskiden yeniye sıralıdır.

## Endpoint'ler

| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/` | API'nin çalıştığını gösteren mesaj |
| POST | `/targets` | Yeni site ekler. Gövde: `{"name": "...", "url": "..."}`. URL zaten varsa `400` döner |
| GET | `/targets` | Tüm siteleri, geçmiş kontrol sonuçlarıyla birlikte listeler |
| GET | `/targets/{id}` | Tek bir sitenin detayını getirir; yoksa `404` döner |
| DELETE | `/targets/{id}` | Siteyi ve ona ait tüm kontrol sonuçlarını siler; yoksa `404` döner |
| GET | `/checks?limit=50` | Son kontrol sonuçlarını en yeniden eskiye sıralı getirir (varsayılan 50 adet) |
| GET | `/dashboard` | `index.html` dashboard sayfasını döndürür |

FastAPI'nin otomatik dokümantasyonu: `http://127.0.0.1:8000/docs`

## Kontrol Mantığı

1. Sunucu açılırken (`lifespan`) bir `BackgroundScheduler` başlatılır ve `run_all_checks` fonksiyonu **30 saniyede bir** çalışacak şekilde ayarlanır. İlk kontrol beklemeden, sunucu açılır açılmaz bir kez yapılır.
2. `run_all_checks`, veritabanındaki tüm siteleri alır ve her biri için `check_target` fonksiyonunu çağırır.
3. `check_target`, siteye tarayıcı `User-Agent` başlığıyla bir HTTP GET isteği atar (**timeout: 10 saniye**) ve süreyi milisaniye olarak ölçer.
   - Cevap geldi ve `status_code < 400` → **UP** (`is_up = True`)
   - Cevap geldi ama `status_code >= 400` → **DOWN**, `error_message = "HTTP <kod>"`
   - Timeout, DNS veya bağlantı hatası (`requests.RequestException`) → **DOWN**, `status_code` boş, hata metni kaydedilir
4. Her sonuç `check_results` tablosuna kaydedilir.

Dashboard (`index.html`) verileri her 10 saniyede bir `GET /targets` ile yeniler ve her sitenin son kontrolünü gösterir. Dashboard'dan site eklenebilir ve silinebilir.

## Kurulum ve Çalıştırma

```bash
git clone https://github.com/enesylvcl/uptime-monitor-api.git
cd uptime-monitor-api

# (İsteğe bağlı) sanal ortam
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

- API: `http://127.0.0.1:8000`
- Dashboard: `http://127.0.0.1:8000/dashboard`
- Swagger dokümantasyonu: `http://127.0.0.1:8000/docs`

`uptime.db` dosyası ilk çalıştırmada otomatik oluşturulur.
