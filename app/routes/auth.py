from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, HTMLResponse
from app.dependencies import templates
from starlette.status import HTTP_302_FOUND
from app.models import User
from app.dependencies import get_password_hash, verify_password, create_access_token, get_db, get_current_user, get_user


router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
async def show_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):

    existing_user = await db.execute(select(User).where(User.username == username))
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.add(new_user)
    await db.commit()

    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.post("/token")
async def token(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user(db, username=request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username}


@router.get("/login", response_class=HTMLResponse, )
async def show_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        error_message = "Invalid username or password"
        return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message})

    access_token = create_access_token(data={"username": user.username})

    response = RedirectResponse(url="/profile", status_code=HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


@router.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    context = {"request": request, "user": user}
    return templates.TemplateResponse("profile.html", context)
