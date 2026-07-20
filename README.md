# Fit Raport

Aplikacja webowa do śledzenia parametrów zdrowotnych: masy ciała, BMI, ciśnienia krwi, tętna
i poziomu cukru. Dashboard z ogólnym podsumowaniem, szczegółowe raporty per parametr (wykres,
historia, statystyki), ręczne wprowadzanie wyników oraz REST API do automatyzacji.

## Stack

FastAPI + SQLAlchemy/Alembic + SQLite + Jinja2/Alpine.js/Chart.js, całość uruchamiana przez Docker.

## Uruchomienie (Docker)

```bash
cp .env.example .env   # opcjonalnie ustaw własny SECRET_KEY
docker compose up --build
```

Aplikacja dostępna pod `http://localhost:8000`. Dane trzymane są w wolumenie `fit_raport_data`
(plik SQLite), więc przetrwają restart kontenera.

## Uruchomienie lokalnie (bez Dockera)

```bash
python -m venv .venv
.venv/Scripts/activate           # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Testy

```bash
pytest
```

## Najważniejsze ścieżki

- `/` — dashboard z podsumowaniem wszystkich parametrów
- `/reports/{waga|bmi|cisnienie|tetno|cukier}` — szczegółowy raport z wykresem i historią
- `/account` — profil (wzrost do wyliczenia BMI) i zarządzanie kluczami API
- `/docs` — dokumentacja Swagger dla REST API
- `/api/v1/{weight|blood-pressure|heart-rate|glucose}` — REST API (autoryzacja nagłówkiem `X-API-Key`)

## Uwaga

Kategorie/klasyfikacje wyników (np. "nadciśnienie", "stan przedcukrzycowy") są orientacyjne,
oparte na standardowych progach referencyjnych, i nie zastępują konsultacji lekarskiej.

## Plan na przyszłość

Nieuwzględnione w MVP, możliwe do dodania później: integracje z urządzeniami/aplikacjami
zewnętrznymi (Fitbit, Garmin, Apple Health, Google Fit) przez OAuth, eksport danych (CSV/PDF),
przypomnienia o pomiarach, wielojęzyczność UI.
