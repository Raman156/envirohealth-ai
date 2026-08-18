from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest
from app.services.user_service import create_user, authenticate_user, get_user_by_email
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await create_user(db, data)
    token = create_access_token(str(user.id))
    return Token(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, anonymous_id=user.anonymous_id, role=user.role),
    )


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return Token(
        access_token=token,
        user=UserResponse(id=user.id, email=user.email, anonymous_id=user.anonymous_id, role=user.role),
    )
