from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.models.file import File
from app.schemas.file import FileRead
from app.services.crud import CRUDBase

file_service = CRUDBase(File)

router = APIRouter(prefix="/sessions/{session_id}/files", tags=["files"])


@router.post("", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    session_id: str, upload: UploadFile, session: AsyncSession = Depends(get_session)
):
    content = await upload.read()
    upload_dir = settings.UPLOAD_DIR / session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / (upload.filename or "untitled")
    file_path.write_bytes(content)

    data = {
        "filename": upload.filename or "untitled",
        "original_name": upload.filename or "untitled",
        "mime_type": upload.content_type,
        "size_bytes": len(content),
        "storage_path": str(file_path),
        "session_id": session_id,
    }
    return await file_service.create(session, data)


@router.get("", response_model=list[FileRead])
async def list_files(
    session_id: str, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    return await file_service.list(
        session, parent_field="session_id", parent_id=session_id, skip=skip, limit=limit
    )


@router.get("/{file_id}", response_model=FileRead)
async def get_file(file_id: str, _=None, session: AsyncSession = Depends(get_session)):
    obj = await file_service.get(session, file_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return obj


@router.get("/{file_id}/download")
async def download_file(file_id: str, session: AsyncSession = Depends(get_session)):
    obj = await file_service.get(session, file_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    path = Path(obj.storage_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        path,
        media_type=obj.mime_type or "application/octet-stream",
        filename=obj.original_name,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str, session: AsyncSession = Depends(get_session)):
    obj = await file_service.get(session, file_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    path = Path(obj.storage_path)
    if path.exists():
        path.unlink()
    await session.delete(obj)
    await session.commit()
