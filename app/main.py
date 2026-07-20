from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import account, api_v1, auth, dashboard, reports

app = FastAPI(title="Fit Raport", description="Śledzenie parametrów zdrowotnych")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    max_age=settings.session_max_age_seconds,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(account.router)
app.include_router(api_v1.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
