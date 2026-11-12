from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_access_token, get_password_hash
from app.db.models import User

security_bearer = HTTPBearer(auto_error=False)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_default_user(db: Session) -> User:
    """Return active demo consumer user or create it if missing."""
    user = db.query(User).filter(User.email == "consumer@powerpulse.in", User.deleted_at.is_(None)).first()
    if not user:
        user = User(
            id="user_default",
            email="consumer@powerpulse.in",
            hashed_password=get_password_hash("PowerPulse123!"),
            full_name="Consumer",
            state="Telangana",
            city="Hyderabad",
            utility="TGSPDCL",
            tariff_category="LT-I(A)",
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.email == "consumer@powerpulse.in").first()
    return user

def get_or_create_guest_user(db: Session, guest_key: str) -> User:
    """Return an isolated per-browser guest profile so visitors never see old/shared test bills."""
    safe_id = "".join(c for c in guest_key if c.isalnum() or c in ("_", "-"))[:36] or "guest_default"
    guest_email = f"{safe_id}@guest.powerpulse.in"
    user = db.query(User).filter(User.id == safe_id, User.deleted_at.is_(None)).first()
    if not user:
        user = db.query(User).filter(User.email == guest_email, User.deleted_at.is_(None)).first()
    if not user:
        user = User(
            id=safe_id,
            email=guest_email,
            hashed_password=get_password_hash("PowerPulse123!"),
            full_name="Consumer",
            state="Telangana",
            city="Hyderabad",
            utility="TGSPDCL",
            tariff_category="LT-I(A)",
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            user = db.query(User).filter(User.id == safe_id).first()
    return user


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    if auth and auth.credentials and auth.credentials not in ("null", "undefined", "demo_token"):
        if auth.credentials.startswith("guest_"):
            guest_user = get_or_create_guest_user(db, auth.credentials)
            if guest_user:
                return guest_user
        payload = decode_access_token(auth.credentials)
        if payload and payload.get("sub"):
            user_id: str = payload.get("sub")
            user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
            if user:
                return user

    # Fallback to default demo user for legacy clients
    default_user = get_or_create_default_user(db)
    if default_user:
        return default_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authorization header missing or invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_optional_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not auth or not auth.credentials or auth.credentials in ("null", "undefined", "demo_token"):
        return get_or_create_default_user(db)
    payload = decode_access_token(auth.credentials)
    if not payload:
        return get_or_create_default_user(db)
    user_id = payload.get("sub")
    return db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()


