from fastapi import FastAPI
from .database import engine, Base, database
from .routes import auth, files, admin


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(on_startup=[init_db, database.connect], on_shutdown=[database.disconnect])


app.include_router(auth.router)
app.include_router(files.router)
app.include_router(admin.router)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the async file-sharing service"}
