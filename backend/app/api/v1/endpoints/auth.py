from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from app.db.models import User, Consent
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        if existing.deleted_at is not None:
            # Re-activate soft-deleted user
            existing.deleted_at = None
            existing.hashed_password = get_password_hash(user_in.password)
            existing.full_name = user_in.full_name
            existing.state = user_in.state or existing.state
            existing.city = user_in.city or existing.city
            existing.utility = user_in.utility or existing.utility
            db.commit()
            access_token = create_access_token(existing.id)
            return Token(
                access_token=access_token,
                user_id=existing.id,
                email=existing.email,
                full_name=existing.full_name
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already registered"
        )
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        state=user_in.state or "Telangana",
        city=user_in.city or "Hyderabad",
        utility=user_in.utility or "TGSPDCL",
        tariff_category=user_in.tariff_category or "LT-I(A)"
    )
    db.add(user)
    db.flush()

    # Record explicit consent
    consent = Consent(
        user_id=user.id,
        consent_type="TERMS_AND_DATA_PROCESSING",
        granted=user_in.consent_granted
    )
    db.add(consent)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id)
    return Token(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email, User.deleted_at.is_(None)).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user.id)
    return Token(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )

