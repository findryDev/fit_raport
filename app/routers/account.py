from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.user import ApiKey, User
from app.services.security import generate_api_key
from app.templating import templates

router = APIRouter(prefix="/account")


@router.get("")
def account_page(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc()).all()
    new_key = request.session.pop("new_api_key", None)
    return templates.TemplateResponse(
        "account.html",
        {"request": request, "user": user, "api_keys": api_keys, "new_key": new_key},
    )


@router.post("/profile")
def update_profile(
    request: Request,
    height_cm: float | None = Form(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.height_cm = height_cm
    db.commit()
    return RedirectResponse("/account", status_code=303)


@router.post("/api-keys")
def create_api_key(
    request: Request,
    name: str = Form(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw_key, key_hash, key_prefix = generate_api_key()
    api_key = ApiKey(user_id=user.id, name=name.strip() or "Klucz API", key_hash=key_hash, key_prefix=key_prefix)
    db.add(api_key)
    db.commit()

    request.session["new_api_key"] = raw_key
    return RedirectResponse("/account", status_code=303)


@router.post("/api-keys/{key_id}/delete")
def delete_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    if api_key:
        db.delete(api_key)
        db.commit()
    return RedirectResponse("/account", status_code=303)
