from fastapi import FastAPI, Request, Depends
from app.dependencies import templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from .database import engine, Base, database
from .routes import auth, files, admin
from .models import User
from .dependencies import get_current_user


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(on_startup=[init_db, database.connect], on_shutdown=[database.disconnect])
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


app.include_router(auth.router)
app.include_router(files.router)
app.include_router(admin.router)


@app.get("/")
async def read_root(request: Request, user: User = Depends(get_current_user)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login")
    contex = {"request": request, "user": user}
    return templates.TemplateResponse("index.html", contex)
