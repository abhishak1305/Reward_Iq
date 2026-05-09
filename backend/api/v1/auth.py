"""Auth API router — register, login, refresh token."""

from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user_id,
)
from backend.models.user import User, UserRole
from backend.models.employee import Employee
from backend.schemas.user import UserCreate, UserLogin, UserOut, TokenResponse, TokenRefresh, UserPasswordUpdate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check duplicate email
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(  # type: ignore[call-arg]
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.employee,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 9.2 Fix: Auto-create Employee profile so /employees/me works immediately
    employee = Employee(  # type: ignore[call-arg]
        user_id=user.id,
        full_name=payload.full_name or payload.email.split('@')[0].replace('.', ' ').title(),
        department=payload.department or "General",
        position=payload.position or "New Employee",
        hire_date=date.today(),
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    # Tokens
    token_extra = {"role": user.role.value, "email": user.email}
    access = create_access_token(user.id, extra=token_extra)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    token_extra = {"role": user.role.value, "email": user.email}
    access = create_access_token(user.id, extra=token_extra)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: TokenRefresh, db: AsyncSession = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    user = await db.get(User, int(data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    # 9.3 Fix: Reject refresh tokens issued before the revocation timestamp
    if user.token_issued_after:
        from datetime import datetime, timezone
        revocation_ts = user.token_issued_after
        if revocation_ts.tzinfo is None:
            revocation_ts = revocation_ts.replace(tzinfo=timezone.utc)
            
        token_iat = datetime.fromtimestamp(data.get("iat", 0), tz=timezone.utc)
        if token_iat < revocation_ts:
            raise HTTPException(status_code=401, detail="Refresh token has been revoked.")

    token_extra = {"role": user.role.value, "email": user.email}
    access = create_access_token(user.id, extra=token_extra)
    new_refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        user=UserOut.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """Revokes the current user's session by bumping token_issued_after."""
    from datetime import datetime, timezone
    user = await db.get(User, user_id)
    if user:
        user.token_issued_after = datetime.now(tz=timezone.utc)
        await db.commit()
    return None


@router.get("/me", response_model=UserOut)
async def me(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return UserOut.model_validate(user)
@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    payload: UserPasswordUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Updates the user's password and revokes all active sessions."""
    from datetime import datetime, timezone
    user = await db.get(User, user_id)
    if not user or not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid current password.")
    
    user.password_hash = hash_password(payload.new_password)
    # Revoke existing sessions on password change
    user.token_issued_after = datetime.now(tz=timezone.utc)
    
    await db.commit()
    return None
