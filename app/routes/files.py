from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
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
