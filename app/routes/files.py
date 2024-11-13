import os
from app.dependencies import templates
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Request, Form
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from app.models import File, User
from app.dependencies import get_db, get_current_user, oauth2_scheme
from starlette.responses import HTMLResponse, RedirectResponse
from app.schemas import FileOut
router = APIRouter()

UPLOAD_FOLDER = 'app/static/uploads/'


@router.get("/upload", response_class=HTMLResponse)
async def read_upload(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request,
                      uploaded_file: UploadFile = Form(...),
                      db: AsyncSession = Depends(get_db),
                      user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can upload files")

    # Проверка существования файла
    result = await db.execute(select(File).filter(File.filename == uploaded_file.filename))
    existing_file = result.scalar_one_or_none()
    if existing_file:
        error_message = "File with this name already exists in the database"
        return templates.TemplateResponse("upload.html", {"request": request, "error_message": error_message})

    # Сохранение файла
    file_path = f"app/media/uploads/{uploaded_file.filename}"
    with open(file_path, "wb") as f:
        f.write(await uploaded_file.read())

    new_file = File(filename=uploaded_file.filename, path=file_path, owner_id=user.id)
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)

    response = RedirectResponse(url="/files", status_code=status.HTTP_302_FOUND)
    return response


@router.get("/files")
async def get_files(request: Request,
                    user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can see all files")

    result = await db.execute(select(File))
    files_db = result.scalars().all()
    files = [{"id": file.id,
              "filename": file.filename,
              "path": file.path,
              "upload_count": file.upload_count,
              "access_granted": file.access_granted,
              "owner_id": file.owner.username} for file in files_db]
    context = {"request": request, "files": files, "user": user}
    return templates.TemplateResponse("files.html", context)


@router.put("/files/{id}")
async def update_file(id: int, request: FileOut, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can change files.")

    # Проверка наличия файла
    result = await db.execute(select(File).filter(File.id == id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Обновление данных
    file.access_granted = request.access_granted
    await db.commit()

    return {"message": "File updated successfully"}


@router.get("/files/users")
async def get_files(request: Request,
                    user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(File).where(File.access_granted == True))
    files_db = result.scalars().fetchall()
    files = [{"id": file.id,
              "filename": file.filename,
              "path": file.path,
              "upload_count": file.upload_count,
              "access_granted": file.access_granted,
              "owner_id": file.owner.username} for file in files_db if file.access_granted is True]
    context = {"request": request, "files": files, "user": user}
    return templates.TemplateResponse("files_users.html", context)


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
                      user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete files")
    result = await db.execute(select(File).filter(File.id == file_id))
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    await db.delete(file)
    await db.commit()
    os.remove(file.path)
    response = RedirectResponse(url="/files", status_code=status.HTTP_200_OK)
    return response
