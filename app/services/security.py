import hashlib
import secrets

from passlib.context import CryptContext

# pbkdf2_sha256: czysty Python (stdlib hashlib), bez zewnętrznych rozszerzeń C/Rust
# (bcrypt bywa problematyczny do zbudowania na niektórych architekturach, np. ARM bez Rusta)
_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

API_KEY_PREFIX = "frk_"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(password, hashed_password)


def generate_api_key() -> tuple[str, str, str]:
    """Zwraca (pełny klucz do pokazania raz użytkownikowi, hash do zapisania w DB, prefiks do wyświetlania)."""
    raw = API_KEY_PREFIX + secrets.token_urlsafe(32)
    key_hash = hash_api_key(raw)
    key_prefix = raw[: len(API_KEY_PREFIX) + 8]
    return raw, key_hash, key_prefix


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
