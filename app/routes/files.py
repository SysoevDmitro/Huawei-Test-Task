from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.models import File
import shutil
import os

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/upload/")
async def upload_file(uploaded_file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    file_path = f"app/static/uploads/{uploaded_file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    new_file = File(filename=uploaded_file.filename, path=file_path)
    db.add(new_file)
    await db.commit()

    return {"filename": uploaded_file.filename}
