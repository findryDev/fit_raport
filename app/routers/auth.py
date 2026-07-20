from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.security import hash_password, verify_password
from app.templating import templates

router = APIRouter()


@router.get("/register")
def register_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    height_cm: float | None = Form(default=None),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    error = None
    if password != password_confirm:
        error = "Hasła nie są identyczne."
    elif len(password) < 8:
        error = "Hasło musi mieć co najmniej 8 znaków."
    elif db.query(User).filter(User.email == email).first():
        error = "Konto z tym adresem e-mail już istnieje."

    if error:
        return templates.TemplateResponse(
            "auth/register.html", {"request": request, "error": error}, status_code=400
        )

    user = User(email=email, hashed_password=hash_password(password), height_cm=height_cm)
    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/login")
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Nieprawidłowy e-mail lub hasło."},
            status_code=400,
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
