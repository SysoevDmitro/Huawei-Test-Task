import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from app.models import File, User
from app.dependencies import get_db, get_current_user, oauth2_scheme
from app.schemas import FileOut


router = APIRouter()

UPLOAD_FOLDER = 'app/static/uploads/'


@router.post("/upload", response_model=FileOut)
async def upload_file(uploaded_file: UploadFile,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user),
                      token: str = Depends(oauth2_scheme)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can upload files")

    file_path = f"app/static/uploads/{uploaded_file.filename}"
    with open(file_path, "wb") as f:
        f.write(await uploaded_file.read())

    new_file = File(filename=uploaded_file.filename, path=file_path, owner_id=current_user.id)
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)

    return new_file


@router.get("/files")
async def get_files(current_user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can see all files")

    result = await db.execute(select(File))
    files = result.scalars().all()
    return [{"id": file.id,
             "filename": file.filename,
             "downloads": file.upload_count,
             "access": file.access_granted} for file in files]


@router.get("/download/{file_id}")
async def download_file(file_id: int,
                        current_user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).filter(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not current_user.is_admin:
        if not file.access_granted:
            raise HTTPException(status_code=403, detail="You can not download this file.")
    file.upload_count += 1
    await db.commit()
    return FileResponse(file.path, filename=file.filename)


@router.delete("/delete/{file_id}")
async def delete_file(file_id: int,
                      current_user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete files")
    result = await db.execute(select(File).filter(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    await db.delete(file)
    await db.commit()
    os.remove(file.path)
    return {"detail": "File deleted"}
