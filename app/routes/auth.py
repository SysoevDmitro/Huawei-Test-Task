from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User
from app.schemas import UserCreate
from app.dependencies import get_password_hash, verify_password, create_access_token, get_db, get_current_user, get_user


router = APIRouter()


@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    check_user = await get_user(db, data.username)
    if check_user:
        raise HTTPException(status_code=400, detail="User already registered")
    db_user = User(username=data.username, password=get_password_hash(data.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/token")
async def token(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user(db, username=request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    access_token = create_access_token(data={"username": user.username})
    return {"access_token":access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username}


@router.get("/profile")
async def profile(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}
